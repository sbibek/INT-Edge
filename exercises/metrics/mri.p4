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
register<bit<32>>(3) hop_latency_t;
// [0] = total, [1] = min, [2] = max
register<bit<32>>(3) q_depth_t;
register<bit<48>>(1) last_checked;

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

         hdr.mri.count = hdr.mri.count + 1;
         hdr.swtraces.push_front(1);
        // According to the P4_16 spec, pushed elements are invalid, so we need
        // to call setValid(). Older bmv2 versions would mark the new header(s)
        // valid automatically (P4_14 behavior), but starting with version 1.11,
        // bmv2 conforms with the P4_16 spec.
        bit<32> current_packets;
        bit<32> current_hlt;
        bit<32> min_hlt;
        bit<32> max_hlt;
        bit<32> current_qdt;
        bit<32> min_qdt;
        bit<32> max_qdt;
        bit<48> current_ts;

        total_packets.read(current_packets, 0);
        hop_latency_t.read(current_hlt, 0);
        hop_latency_t.read(min_hlt , 1);
        hop_latency_t.read(max_hlt , 2);
        q_depth_t.read(current_qdt,0);
        q_depth_t.read(min_qdt , 1);
        q_depth_t.read(max_qdt , 2);
        last_checked.read(current_ts, 0);


        hdr.swtraces[0].setValid();
        hdr.swtraces[0].swid = swid;
        hdr.swtraces[0].total_packets = current_packets;
        hdr.swtraces[0].elapsed_time = (bit<32>) (standard_metadata.egress_global_timestamp - current_ts);
        hdr.swtraces[0].total_hop_latency = current_hlt;
        hdr.swtraces[0].min_hop_latency = min_hlt;
        hdr.swtraces[0].max_hop_latency = max_hlt;
        hdr.swtraces[0].total_qdepth = current_qdt;
        hdr.swtraces[0].min_qdepth = min_qdt;
        hdr.swtraces[0].max_qdepth = max_qdt;

        // now we rest the registers
        total_packets.write(0, 0);
        hop_latency_t.write(0, 0);
        hop_latency_t.write(1, 0);
        hop_latency_t.write(2, 0);
        q_depth_t.write(0 , 0);
        q_depth_t.write(1, 0);
        q_depth_t.write(2, 0);
        last_checked.write(0, standard_metadata.egress_global_timestamp);
        init.write(0, (bit<1>)0);

        hdr.udp.length_ = hdr.udp.length_ + 36;
    	hdr.ipv4.totalLen = hdr.ipv4.totalLen + 36;


    }

    action add_linktrace(switchID_t swid) {
        hdr.ipv4_option.swid = (bit<16>)swid;
        hdr.ipv4_option.reference_timestamp = standard_metadata.egress_global_timestamp;
    }

    action remove_linktrace() {
        if(hdr.ipv4_option.isValid()) {
            hdr.ipv4.ihl = hdr.ipv4.ihl - 2 ;
            hdr.ipv4.totalLen = hdr.ipv4.totalLen - 8;
        }

        hdr.ipv4_option.setInvalid();
    }

    table swtrace {
        actions = { 
	    add_swtrace; 
	    NoAction; 
        }
        default_action = NoAction();      
    }

    table linktrace {
        actions = {
            add_linktrace;
            NoAction;
        }
        default_action = NoAction();
    }

    table unlinktrace {
        key= {
            standard_metadata.egress_port: exact;
        }
        actions = {
            remove_linktrace;
            NoAction;
        }
        default_action = remove_linktrace();
    }
    
    apply {

        @atomic {
        bit<1> isInit;
        init.read(isInit, 0);
        if(isInit == 0) {
            // next time its 1 
            init.write(0, (bit<1>)1);
        }

        // we update the registers here everytime
        bit<32> current_packets;
        total_packets.read(current_packets, 0);
        total_packets.write(0, current_packets+1);


        bit<32> current_hlt;
        hop_latency_t.read(current_hlt, 0);
        hop_latency_t.write(0, current_hlt + (bit<32>)standard_metadata.deq_timedelta);

        bit<32> min_hlt;
        hop_latency_t.read(min_hlt , 1);
        if(isInit == 0) {
            hop_latency_t.write(1, (bit<32>)standard_metadata.deq_timedelta);
        } else if(min_hlt > (bit<32>)standard_metadata.deq_timedelta) {
            hop_latency_t.write(1, (bit<32>)standard_metadata.deq_timedelta);
        }

        bit<32> max_hlt;
        hop_latency_t.read(max_hlt , 2);
        if(isInit == 0) {
            hop_latency_t.write(2, (bit<32>)standard_metadata.deq_timedelta);
        } else if(max_hlt < (bit<32>)standard_metadata.deq_timedelta) {
            hop_latency_t.write(2, (bit<32>)standard_metadata.deq_timedelta);
        }


        bit<32> current_qdt;
        q_depth_t.read(current_qdt,0);
        q_depth_t.write(0, current_qdt + (bit<32>)standard_metadata.deq_qdepth );


        bit<32> min_qdt;
        q_depth_t.read(min_qdt , 1);
        if(isInit == 0) {
            q_depth_t.write(1, (bit<32>)standard_metadata.deq_qdepth);
        } else if(min_qdt > (bit<32>)standard_metadata.deq_qdepth) {
            q_depth_t.write(1, (bit<32>)standard_metadata.deq_qdepth);
        }

        bit<32> max_qdt;
        q_depth_t.read(max_qdt , 2);
        if(isInit == 0) {
            q_depth_t.write(2, (bit<32>)standard_metadata.deq_qdepth);
        } else if(max_qdt < (bit<32>)standard_metadata.deq_qdepth) {
            q_depth_t.write(2, (bit<32>)standard_metadata.deq_qdepth);
        }

        bit<48> current_ts;
        last_checked.read(current_ts, 0);
        if(current_ts == 0) {
            last_checked.write(0, standard_metadata.egress_global_timestamp);
        }


      
        //----------------------------
        if(!hdr.ipv4_option.isValid()) {
            hdr.ipv4_option.setValid();
            hdr.ipv4.ihl = hdr.ipv4.ihl + 2 ;
            hdr.ipv4.totalLen = hdr.ipv4.totalLen + 8;
        }

        linktrace.apply();
        unlinktrace.apply();

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
