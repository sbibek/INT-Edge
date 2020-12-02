/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "include/common.p4"
#include "include/headers.p4"
#include "include/parser.p4"
#include "include/checksum.p4"




register<bit<1>>(1) init;
register<bit<32>>(1) total_packets;
// [0] = total, [1] = min, [2] = max
register<bit<32>>(1) hop_latency_t;
// [0] = total, [1] = min, [2] = max
register<bit<32>>(1) q_depth_t;
register<bit<48>>(1) last_checked;

register<bit<32>>(MAX_HOPS) link_latency_t;

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
            hdr.mri_fork.fork: exact;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {
        if (hdr.ipv4.isValid()) {
            ipv4_lpm.apply();
        }
    }
}


control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    action add_swtrace(switchID_t swid) { 

        // add information to the option regarding the current timestamp
        hdr.ipv4_option.swid = (bit<8>)swid;
        hdr.ipv4_option.reference_timestamp = standard_metadata.egress_global_timestamp;

         hdr.mri.count = hdr.mri.count + 1;
         hdr.swtraces.push_front(1);
        // According to the P4_16 spec, pushed elements are invalid, so we need
        // to call setValid(). Older bmv2 versions would mark the new header(s)
        // valid automatically (P4_14 behavior), but starting with version 1.11,
        // bmv2 conforms with the P4_16 spec.
        bit<32> current_packets;
        bit<32> current_hlt;
        bit<32> current_qdt;
        bit<48> current_ts;

        total_packets.read(current_packets, 0);
        hop_latency_t.read(current_hlt, 0);
        q_depth_t.read(current_qdt,0);
        last_checked.read(current_ts, 0);


        hdr.swtraces[0].setValid();
        hdr.swtraces[0].swid = (bit<8>)swid;
        hdr.swtraces[0].total_packets = current_packets;
        hdr.swtraces[0].total_hop_latency = current_hlt;
        hdr.swtraces[0].total_qdepth =(bit<16>)current_qdt;

        bit<32> link_latency;
        link_latency_t.read(link_latency, 0);
        hdr.swtraces[0].l1_info.swid = 0;
        hdr.swtraces[0].l1_info.totalLatency = (bit<16>)link_latency;

        link_latency_t.read(link_latency, 1);
        hdr.swtraces[0].l2_info.swid = 1;
        hdr.swtraces[0].l2_info.totalLatency = (bit<16>)link_latency;

        link_latency_t.read(link_latency, 2);
        hdr.swtraces[0].l3_info.swid = 2;
        hdr.swtraces[0].l3_info.totalLatency = (bit<16>)link_latency;

        link_latency_t.read(link_latency, 3);
        hdr.swtraces[0].l4_info.swid = 3;
        hdr.swtraces[0].l4_info.totalLatency = (bit<16>)link_latency;

        link_latency_t.read(link_latency, 4);
        hdr.swtraces[0].l5_info.swid = 4;
        hdr.swtraces[0].l5_info.totalLatency = (bit<16>)link_latency;

        // now we rest the registers
        total_packets.write(0, 0);
        hop_latency_t.write(0, 0);
        q_depth_t.write(0 , 0);

        link_latency_t.write(0,0);
        link_latency_t.write(1,0);
        link_latency_t.write(2,0);
        link_latency_t.write(3,0);
        link_latency_t.write(4,0);

        hdr.udp.length_ = hdr.udp.length_ + 26;
    	hdr.ipv4.totalLen = hdr.ipv4.totalLen + 26;
    }

    table swtrace {
        actions = { 
	    add_swtrace; 
	    NoAction; 
        }
        default_action = NoAction();      
    }

    apply {

        @atomic {

        // we update the registers here everytime
        bit<32> current_packets;
        total_packets.read(current_packets, 0);
        total_packets.write(0, current_packets+1);


        bit<32> current_hlt;
        hop_latency_t.read(current_hlt, 0);
        hop_latency_t.write(0, current_hlt + (bit<32>)standard_metadata.deq_timedelta);



        bit<32> current_qdt;
        q_depth_t.read(current_qdt,0);
        q_depth_t.write(0, current_qdt + (bit<32>)standard_metadata.deq_qdepth );


      
        //----------------------------
        if(hdr.ipv4_option.isValid() && hdr.ipv4_option.option == IPV4_OPTION_MRI) {
            // extract the information
            bit<32> current_latency = (bit<32>)(standard_metadata.ingress_global_timestamp - hdr.ipv4_option.reference_timestamp);
            link_latency_t.write((bit<32>)hdr.ipv4_option.swid, current_latency );

        }

        if (hdr.mri.isValid()) {
            swtrace.apply();
        } 

        }
    }
}



/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.ipv4_option);
        packet.emit(hdr.udp);
        packet.emit(hdr.mri_fork);
        packet.emit(hdr.mri);
        packet.emit(hdr.swtraces);                 
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
