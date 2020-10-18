/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "include/common.p4"
#include "include/headers.p4"
#include "include/parser.p4"
#include "include/checksum.p4"





/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

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

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    action add_swtrace(switchID_t swid) { 
        //  if(!hdr.mri.isValid()) {
        //      hdr.mri.count = 0
        //  }

         hdr.mri.count = hdr.mri.count + 1;
         hdr.swtraces.push_front(1);
        // According to the P4_16 spec, pushed elements are invalid, so we need
        // to call setValid(). Older bmv2 versions would mark the new header(s)
        // valid automatically (P4_14 behavior), but starting with version 1.11,
        // bmv2 conforms with the P4_16 spec.
         hdr.swtraces[0].setValid();
         hdr.swtraces[0].swid = swid;
         hdr.swtraces[0].qdepth = (qdepth_t)standard_metadata.deq_qdepth;
         hdr.swtraces[0].hoplatency = (hoplatency_t) standard_metadata.deq_timedelta;
         hdr.swtraces[0].linklatency = (linklatency_t) standard_metadata.egress_global_timestamp;

         if(hdr.mri.count > 1) {
             hdr.swtraces[0].linklatency = (linklatency_t) (standard_metadata.ingress_global_timestamp - hdr.swtraces[1].refTimestamp);
         } else {
            hdr.swtraces[0].linklatency = (linklatency_t)0;
         }

         // need to put egress timestamp anyway
         hdr.swtraces[0].refTimestamp = standard_metadata.egress_global_timestamp;

         hdr.udp.length_ = hdr.udp.length_ + 22;

         //hdr.ipv4.ihl = hdr.ipv4.ihl + 3;
         //hdr.ipv4_option.optionLength = hdr.ipv4_option.optionLength + 12; 
    	hdr.ipv4.totalLen = hdr.ipv4.totalLen + 22;

    }

    table swtrace {
        actions = { 
	    add_swtrace; 
	    NoAction; 
        }
        default_action = NoAction();      
    }
    
    apply {
        if (hdr.mri.isValid()) {
            swtrace.apply();
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
        // packet.emit(hdr.ipv4_option);
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
