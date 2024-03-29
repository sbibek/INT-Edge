/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "include/common.p4"
#include "include/headers.p4"
#include "include/parser.p4"
#include "include/checksum.p4"


#define RE_HASH(inc) if(atIdx != (bit<32>)hdr.ipv4_option.swid && atIdx != (bit<32>)0) { \
                rand = rand + (bit<32>)hdr.ipv4_option.swid + (bit<32>)inc; \
                hash(idx, HashAlgorithm.crc32, (bit<32>)0, {hdr.ipv4_option.swid, rand},(bit<32>) MAX_NEIGHBORS); \
                swid_map_t.read(atIdx, idx); \
            }

#define UPDATE_PAYLOAD_FROM_REG(idx) link_latency_t.read(link_latency, idx); \
                                swid_map_t.read(sid, idx); \
                                hdr.swtraces[0].l##idx##_info.swid = (bit<8>)sid; \
                                hdr.swtraces[0].l##idx##_info.totalLatency = (bit<16>)link_latency; 

#define UPDATE_QD_FROM_REG(idx) qdepthall_t.read(qd_egress, idx); \
                                hdr.swtraces[0].p##idx##_qd = (bit<32>)qd_egress;


register<bit<32>>(1) total_packets;
register<bit<32>>(1) hop_latency_t;
register<bit<32>>(1) q_depth_t;
register<bit<32>>(1) max_qdepth_t;

register<bit<32>>(255) hash_rand_t;
register<bit<32>>(MAX_NEIGHBORS) swid_map_t;
register<bit<32>>(MAX_NEIGHBORS) link_latency_t;

register<bit<32>>(5) qdepthall_t;

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
            // hdr.mri_fork.fork: exact;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    table probe_lpm {
        key = {
            hdr.ipv4.srcAddr: lpm;
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
        if(hdr.mri.isValid()) {
            probe_lpm.apply();
        }
        else if (hdr.ipv4.isValid()) {
            ipv4_lpm.apply();
        }
    }
}


control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    action add_swtrace(switchID_t swid) { 

        // qdepthall_t.write((bit<32>)standard_metadata.egress_port, (bit<32>)swid);

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
        bit<32> max_qdt;

        total_packets.read(current_packets, 0);
        hop_latency_t.read(current_hlt, 0);
        q_depth_t.read(current_qdt,0);
        max_qdepth_t.read(max_qdt, 0);


        hdr.swtraces[0].setValid();
        hdr.swtraces[0].swid = (bit<8>)swid;
        hdr.swtraces[0].total_packets = current_packets;
        hdr.swtraces[0].total_hop_latency = current_hlt;
        hdr.swtraces[0].total_qdepth =(bit<16>)max_qdt;

        bit<32> link_latency;
        bit<32> sid;

        UPDATE_PAYLOAD_FROM_REG(0);
        UPDATE_PAYLOAD_FROM_REG(1);
        UPDATE_PAYLOAD_FROM_REG(2);
        UPDATE_PAYLOAD_FROM_REG(3);
        UPDATE_PAYLOAD_FROM_REG(4);

        bit<32> qd_egress;
        UPDATE_QD_FROM_REG(0);
        UPDATE_QD_FROM_REG(1);
        UPDATE_QD_FROM_REG(2);
        UPDATE_QD_FROM_REG(3);
        UPDATE_QD_FROM_REG(4);

        // now we rest the registers
        total_packets.write(0, 0);
        hop_latency_t.write(0, 0);
        q_depth_t.write(0 , 0);
        max_qdepth_t.write(0, 0);
        qdepthall_t.write(0, 0);
        qdepthall_t.write(1, 0);
        qdepthall_t.write(2, 0);
        qdepthall_t.write(3, 0);
        qdepthall_t.write(4, 0);

        hdr.udp.length_ = hdr.udp.length_ + 46;
    	hdr.ipv4.totalLen = hdr.ipv4.totalLen + 46;
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

        bit<32> current_max_qdt;
        max_qdepth_t.read(current_max_qdt, 0);
        if((bit<32>)standard_metadata.deq_qdepth > current_max_qdt) {
                // means we update
            max_qdepth_t.write(0, (bit<32>)standard_metadata.deq_qdepth);
        }
        

        bit<32> qdepth_for_egress;
        qdepthall_t.read(qdepth_for_egress, (bit<32>)standard_metadata.egress_port);
        if((bit<32>)standard_metadata.deq_qdepth > qdepth_for_egress) {
            qdepthall_t.write((bit<32>)standard_metadata.egress_port, (bit<32>)standard_metadata.deq_qdepth);
        }
        
      
        //----------------------------
        if(hdr.ipv4_option.isValid() && hdr.ipv4_option.option == IPV4_OPTION_MRI && hdr.ipv4_option.reference_timestamp != 0) {
            // reference timestamp is 0 only when the switch receiving it is the fist switch from the sender host
            // in that case we can just ignore the info at that case
            // extract the information
            bit<32> current_latency = (bit<32>)(standard_metadata.ingress_global_timestamp - hdr.ipv4_option.reference_timestamp);
            // we only store MAX_NEIGHBORS

            // this way of generating index always might not be good as this might collide as we have small number of neighbors 
            // so we chain the hashing algorithm until we find a good spot, assuming running hash for 5 times is sufficient to land on the 
            // unique index, we will increment the random value for all the reruns
            bit<32> idx;
            bit<32> rand;
            bit<32> atIdx;

            hash_rand_t.read(rand, (bit<32>)hdr.ipv4_option.swid);
            hash(idx, HashAlgorithm.crc32, (bit<32>)0, {hdr.ipv4_option.swid, rand},(bit<32>) MAX_NEIGHBORS);
            swid_map_t.read(atIdx, idx);

            RE_HASH(17);
            RE_HASH(8);
            RE_HASH(21);
            RE_HASH(219);
            RE_HASH(787);

            // now we will take the resultant value of rand as the random used for this switch
            // next time, this same hash will be used to get to the same index
            hash_rand_t.write((bit<32>) hdr.ipv4_option.swid, rand);

            // now push data to those idx
            swid_map_t.write(idx, (bit<32>)hdr.ipv4_option.swid);
            link_latency_t.write(idx, current_latency );
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
