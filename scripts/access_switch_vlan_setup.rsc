# Config to setup 3 VLANS id=100 on ether2, id=10 on ether3, id=20 on ether4
# ether2, ether3, ether4 are access ports
# ether1 is a trunk port

/interface bridge
add ingress-filtering=no name=bridge1 vlan-filtering=yes
/interface bridge port
add bridge=bridge1 interface=ether2 pvid=100
add bridge=bridge1 interface=ether3 pvid=10
add bridge=bridge1 interface=ether4 pvid=20
add bridge=bridge1 interface=ether1
/interface bridge vlan
add bridge=bridge1 tagged=ether1 vlan-ids=100
add bridge=bridge1 tagged=ether1 vlan-ids=10
add bridge=bridge1 tagged=ether1 vlan-ids=20
