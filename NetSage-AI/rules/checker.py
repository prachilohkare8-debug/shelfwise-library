import ipaddress
import re


# ============================================================
# INTERFACE
# ============================================================

def check_interface_status(command_output):

    if "administratively down" in command_output.lower():

        return {
            "category": "INTERFACE",
            "issue": "Interface is administratively down",
            "severity": "High"
        }

    return None


# ============================================================
# ROUTING
# ============================================================

def check_missing_route(command_output):

    match = re.search(
        r"No route for ([0-9./]+)",
        command_output,
        re.IGNORECASE
    )

    if match:

        return {
            "category": "ROUTING",
            "issue": f"Missing route to {match.group(1)}",
            "severity": "High"
        }

    if "No gateway of last resort" in command_output:

        return {
            "category": "ROUTING",
            "issue": "Default route is missing",
            "severity": "High"
        }

    return None


def check_route_next_hop(
    expected_next_hop=None,
    actual_next_hop=None
):

    if (
        expected_next_hop
        and actual_next_hop
        and expected_next_hop != actual_next_hop
    ):

        return {
            "category": "ROUTING",
            "issue": (
                f"Incorrect next hop: expected "
                f"{expected_next_hop}, got {actual_next_hop}"
            ),
            "severity": "High"
        }

    return None


def check_route_network(
    expected_route=None,
    actual_route=None
):

    if (
        expected_route
        and actual_route
        and expected_route != actual_route
    ):

        return {
            "category": "ROUTING",
            "issue": (
                f"Incorrect destination network: expected "
                f"{expected_route}, got {actual_route}"
            ),
            "severity": "High"
        }

    return None


# ============================================================
# GATEWAY
# ============================================================

def check_gateway(command_output):

    ip_match = re.search(
        r"IP:\s*([0-9.]+)",
        command_output,
        re.IGNORECASE
    )

    mask_match = re.search(
        r"Subnet Mask:\s*([0-9.]+)",
        command_output,
        re.IGNORECASE
    )

    gateway_match = re.search(
        r"Default Gateway:\s*([0-9.]+)",
        command_output,
        re.IGNORECASE
    )

    if not ip_match or not mask_match or not gateway_match:
        return None

    try:

        ip_address = ipaddress.ip_address(
            ip_match.group(1)
        )

        subnet_mask = ipaddress.ip_address(
            mask_match.group(1)
        )

        gateway = ipaddress.ip_address(
            gateway_match.group(1)
        )

        network = ipaddress.IPv4Network(
            f"{ip_address}/{subnet_mask}",
            strict=False
        )

        if gateway not in network:

            return {
                "category": "GATEWAY",
                "issue": "Default gateway is outside the PC subnet",
                "severity": "High"
            }

    except ValueError:

        return None

    return None


# ============================================================
# VLAN
# ============================================================

def check_vlan(
    expected_vlan=None,
    actual_vlan=None
):

    if (
        expected_vlan is not None
        and actual_vlan is not None
        and str(expected_vlan) != str(actual_vlan)
    ):

        return {
            "category": "VLAN",
            "issue": (
                f"VLAN mismatch: expected VLAN "
                f"{expected_vlan}, actual VLAN {actual_vlan}"
            ),
            "severity": "High"
        }

    return None


def check_missing_vlan(
    expected_vlan=None,
    actual_vlan=None
):

    if (
        expected_vlan is not None
        and actual_vlan is None
        and "not present" in str(expected_vlan).lower()
    ):

        return {
            "category": "VLAN",
            "issue": "Required VLAN is missing",
            "severity": "High"
        }

    return None


def check_vlan_trunk(command_output):

    text = command_output.lower()

    if (
        "administrative mode: static access" in text
        and "operational mode: static access" in text
    ):

        return {
            "category": "VLAN",
            "issue": "Switch-to-switch port is configured as an access port instead of a trunk",
            "severity": "High"
        }

    return None


def check_allowed_vlan(command_output):

    match = re.search(
        r"Allowed VLANs:\s*([0-9,]+)",
        command_output,
        re.IGNORECASE
    )

    if not match:
        return None

    allowed = [
        x.strip()
        for x in match.group(1).split(",")
    ]

    if "30" not in allowed:

        return {
            "category": "VLAN",
            "issue": "VLAN 30 is missing from the trunk allowed VLAN list",
            "severity": "High"
        }

    return None


def check_native_vlan(
    expected_native_vlan=None,
    actual_native_vlan=None
):

    if (
        expected_native_vlan
        and actual_native_vlan
        and str(expected_native_vlan)
        != str(actual_native_vlan)
    ):

        return {
            "category": "VLAN",
            "issue": "Native VLAN mismatch",
            "severity": "High"
        }

    return None


# ============================================================
# DHCP
# ============================================================

def check_dhcp_gateway(
    expected_network=None,
    dhcp_gateway=None
):

    if not expected_network or not dhcp_gateway:
        return None

    try:

        network = ipaddress.ip_network(
            expected_network
        )

        gateway = ipaddress.ip_address(
            dhcp_gateway
        )

        if gateway not in network:

            return {
                "category": "DHCP",
                "issue": (
                    "DHCP default gateway is outside "
                    "the configured LAN subnet"
                ),
                "severity": "High"
            }

    except ValueError:

        return None

    return None


def check_dhcp_network(
    expected_network=None,
    dhcp_network=None
):

    if (
        expected_network
        and dhcp_network
        and expected_network != dhcp_network
    ):

        return {
            "category": "DHCP",
            "issue": (
                f"DHCP pool uses the wrong network: "
                f"expected {expected_network}, "
                f"got {dhcp_network}"
            ),
            "severity": "High"
        }

    return None


def check_dhcp_pool(command_output):

    if "No DHCP pools configured" in command_output:

        return {
            "category": "DHCP",
            "issue": "DHCP pool is missing",
            "severity": "High"
        }

    return None


def check_dhcp_excluded(command_output):

    expected = "192.168.10.1 192.168.10.10"

    if (
        "excluded-address" in command_output
        and "192.168.10.1 192.168.10.5"
        in command_output
    ):

        return {
            "category": "DHCP",
            "issue": "DHCP excluded-address range is incomplete",
            "severity": "Medium"
        }

    return None


def check_server_unreachable(command_output, category):

    if "Destination host unreachable" in command_output:

        return {
            "category": category,
            "issue": f"{category} server is unreachable",
            "severity": "High"
        }

    return None


# ============================================================
# DNS
# ============================================================

def check_dns(
    expected_dns=None,
    actual_dns=None
):

    if (
        expected_dns
        and actual_dns
        and expected_dns != actual_dns
    ):

        return {
            "category": "DNS",
            "issue": (
                f"Incorrect DNS server: expected "
                f"{expected_dns}, got {actual_dns}"
            ),
            "severity": "Medium"
        }

    return None


def check_dns_timeout(command_output):

    if "DNS request timed out" in command_output:

        return {
            "category": "DNS",
            "issue": "DNS name resolution is failing",
            "severity": "Medium"
        }

    return None


# ============================================================
# ACL
# ============================================================

def check_acl_icmp(command_output):

    text = command_output.lower()

    if "deny icmp" in text:

        return {
            "category": "ACL",
            "issue": "ACL blocks ICMP traffic",
            "severity": "High"
        }

    return None


def check_acl_http(command_output):

    text = command_output.lower()

    if (
        "deny tcp" in text
        and "eq 80" in text
    ):

        return {
            "category": "ACL",
            "issue": "ACL blocks HTTP traffic",
            "severity": "High"
        }

    return None


def check_acl_interface(
    expected_acl_interface=None,
    actual_acl_interface=None
):

    if (
        expected_acl_interface
        and actual_acl_interface
        and expected_acl_interface
        != actual_acl_interface
    ):

        return {
            "category": "ACL",
            "issue": "ACL is applied to the wrong interface",
            "severity": "High"
        }

    return None


def check_acl_direction(
    expected_acl_direction=None,
    actual_acl_direction=None
):

    if (
        expected_acl_direction
        and actual_acl_direction
        and expected_acl_direction.lower()
        != actual_acl_direction.lower()
    ):

        return {
            "category": "ACL",
            "issue": "ACL is applied in the wrong direction",
            "severity": "High"
        }

    return None


# ============================================================
# NAT
# ============================================================

def check_nat_missing(command_output):

    if "No translations" in command_output:

        return {
            "category": "NAT",
            "issue": "NAT configuration is missing or not producing translations",
            "severity": "High"
        }

    return None


def check_nat_interfaces(
    expected_inside=None,
    expected_outside=None,
    actual_inside=None,
    actual_outside=None
):

    if (
        expected_inside
        and expected_outside
        and actual_inside
        and actual_outside
    ):

        if (
            expected_inside != actual_inside
            or expected_outside != actual_outside
        ):

            return {
                "category": "NAT",
                "issue": "NAT inside and outside interfaces are reversed",
                "severity": "High"
            }

    return None


def check_nat_overload(
    nat_overload=None
):

    if nat_overload == "missing":

        return {
            "category": "NAT",
            "issue": "NAT overload is missing",
            "severity": "High"
        }

    return None


# ============================================================
# WIRELESS
# ============================================================

def check_wireless_ssid(
    expected_ssid=None,
    actual_ssid=None
):

    if (
        expected_ssid
        and actual_ssid
        and expected_ssid != actual_ssid
    ):

        return {
            "category": "WIRELESS",
            "issue": "Wireless SSID is incorrect",
            "severity": "Medium"
        }

    return None


def check_wireless_security(
    expected_security=None,
    actual_security=None
):

    if (
        expected_security
        and actual_security
        and expected_security.lower()
        != actual_security.lower()
    ):

        return {
            "category": "WIRELESS",
            "issue": "Wireless security configuration is incorrect",
            "severity": "High"
        }

    return None


def check_wireless_dhcp(command_output):

    if "DHCP: Failed" in command_output:

        return {
            "category": "WIRELESS",
            "issue": "Wireless DHCP assignment is failing",
            "severity": "High"
        }

    return None


# ============================================================
# MASTER CHECKER
# ============================================================

def run_all_checks(
    command_output,
    expected_vlan=None,
    actual_vlan=None,
    expected_network=None,
    dhcp_gateway=None,
    dhcp_network=None,
    expected_next_hop=None,
    actual_next_hop=None,
    expected_route=None,
    actual_route=None,
    expected_native_vlan=None,
    actual_native_vlan=None,
    expected_dns=None,
    actual_dns=None,
    expected_acl_interface=None,
    actual_acl_interface=None,
    expected_acl_direction=None,
    actual_acl_direction=None,
    expected_inside=None,
    expected_outside=None,
    actual_inside=None,
    actual_outside=None,
    nat_overload=None,
    expected_ssid=None,
    actual_ssid=None,
    expected_security=None,
    actual_security=None
):

    findings = []

    checks = [

        check_interface_status(
            command_output
        ),

        check_missing_route(
            command_output
        ),

        check_route_next_hop(
            expected_next_hop,
            actual_next_hop
        ),

        check_route_network(
            expected_route,
            actual_route
        ),

        check_gateway(
            command_output
        ),

        check_vlan(
            expected_vlan,
            actual_vlan
        ),

        check_vlan_trunk(
            command_output
        ),

        check_allowed_vlan(
            command_output
        ),

        check_native_vlan(
            expected_native_vlan,
            actual_native_vlan
        ),

        check_dhcp_gateway(
            expected_network,
            dhcp_gateway
        ),

        check_dhcp_network(
            expected_network,
            dhcp_network
        ),

        check_dhcp_pool(
            command_output
        ),

        check_dhcp_excluded(
            command_output
        ),

        check_dns(
            expected_dns,
            actual_dns
        ),

        check_dns_timeout(
            command_output
        ),

        check_acl_icmp(
            command_output
        ),

        check_acl_http(
            command_output
        ),

        check_acl_interface(
            expected_acl_interface,
            actual_acl_interface
        ),

        check_acl_direction(
            expected_acl_direction,
            actual_acl_direction
        ),

        check_nat_missing(
            command_output
        ),

        check_nat_interfaces(
            expected_inside,
            expected_outside,
            actual_inside,
            actual_outside
        ),

        check_nat_overload(
            nat_overload
        ),

        check_wireless_ssid(
            expected_ssid,
            actual_ssid
        ),

        check_wireless_security(
            expected_security,
            actual_security
        ),

        check_wireless_dhcp(
            command_output
        )
    ]

    for result in checks:

        if result:
            findings.append(result)

    return findings
