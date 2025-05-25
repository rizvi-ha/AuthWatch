from csv_helper import get_login_logs
import pandas as pd
from datetime import datetime

CURRENT_COUNTRY = "Taiwan"
VPN_MODE = False

# IP to country mapping (
def resolve_country(ip: str) -> str:
    ip_map = {
        "66.206.89.11": "USA",
        "38.183.48.25": "UK",
        "53.120.67.248": "Taiwan",
        "134.20.151.217": "Taiwan",
        "124.132.128.69": "Taiwan",
        "218.90.33.123": "Japan",
        "218.70.250.234": "Taiwan",
        "134.63.156.154": "Taiwan",
        "222.55.201.154": "Taiwan",
        "144.31.231.185": "Taiwan",
        "214.127.233.122": "Australia",
        "161.94.93.133": "Taiwan",
        "129.141.34.136": "Taiwan",
        "220.109.170.18": "Taiwan",
        "63.204.126.213": "USA",
        "74.131.146.207": "Taiwan",
        "186.174.57.125": "Taiwan",
        "196.189.205.50": "Taiwan",
        "216.35.142.90": "Taiwan",
        "197.8.132.138": "Taiwan",
        "113.157.136.109": "USA",
        "182.129.37.16": "Taiwan",
        "182.187.77.223": "Taiwan",
        "63.165.105.39": "Taiwan",
        "154.51.61.158": "Taiwan",
        "222.109.65.48": "Taiwan",
        "207.183.200.174": "Taiwan",
        "199.49.137.13": "Taiwan",
        "205.234.56.25": "Taiwan",
        "206.87.134.148": "Taiwan",
        "209.114.171.210": "Taiwan",
        "151.214.48.121": "Taiwan",
        "213.38.155.206": "Taiwan",
        "169.71.188.61": "Taiwan",
        "119.74.140.99": "Taiwan",
        "207.117.37.207": "Taiwan",
        "2.202.141.118": "Germany",
        "22.79.23.82": "Taiwan",
        "204.176.42.106": "Taiwan",
        "194.99.174.220": "Taiwan",
        "187.7.179.156": "Taiwan",
        "143.223.218.51": "Taiwan",
        "205.12.121.36": "Taiwan",
        "165.242.48.249": "Taiwan",
        "170.58.33.145": "Taiwan",
        "102.157.160.161": "Taiwan",
        "214.120.11.119": "Taiwan",
        "138.69.32.232": "Taiwan",
        "214.177.197.177": "Taiwan",
        "212.45.91.169": "Taiwan",
        "180.152.194.206": "Taiwan",
        "54.132.245.5": "Taiwan",
        "175.117.240.148": "Taiwan",
        "135.66.7.200": "Taiwan",
        "89.165.121.13": "Taiwan",
        "222.138.190.221": "Taiwan",
        "108.106.201.32": "Taiwan",
        "222.34.249.236": "Taiwan",
        "193.48.128.119": "Taiwan",
        "101.212.115.144": "Taiwan",
        "159.120.131.226": "Taiwan",
        "211.105.73.112": "Taiwan",
        "152.214.72.16": "Taiwan",
        "200.64.249.114": "Taiwan",
        "155.239.201.150": "Taiwan",
        "134.1.221.45": "Taiwan",
        "212.208.124.166": "Taiwan",
        "217.47.246.14": "Taiwan",
        "204.49.253.9": "Taiwan",
        "92.7.26.105": "Taiwan",
        "220.67.34.89": "Taiwan",
        "190.96.106.62": "Taiwan",
        "24.223.136.35": "Taiwan",
        "7.138.242.237": "Taiwan",
        "198.141.131.108": "Taiwan",
        "220.23.112.183": "Taiwan",
        "98.58.11.86": "Taiwan",
        "131.170.51.108": "Taiwan",
        "58.21.91.2": "Taiwan",
        "203.67.31.48": "Taiwan",
        "143.168.248.20": "Taiwan",
        "223.147.68.70": "Taiwan",
        "195.58.232.124": "Taiwan",
        "215.156.15.130": "Taiwan",
        "190.110.93.192": "Taiwan",
        "132.246.226.129": "Taiwan",
        "131.70.84.166": "Taiwan",
        "216.230.231.83": "Taiwan",
        "217.85.190.144": "Taiwan",
        "115.232.39.161": "Taiwan",
        "74.60.80.187": "Taiwan",
        "198.179.120.6": "Taiwan",
        "141.60.189.30": "Taiwan",
        "213.175.2.8": "Taiwan",
        "148.55.94.6": "Taiwan",
        "15.72.245.47": "Taiwan",
        "214.176.22.37": "Taiwan",
    }
    return ip_map.get(ip, "Unknown")

def get_recent_alerts(limit: int = 10, vpn_mode=False, allowed_country="Taiwan") -> list[dict]:
    df = get_login_logs()
    if df.empty:
        return []

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    alerts = []

    # multiple failed login attempts from the same IP
    failed_df = df[df["login_result"] == False]
    fail_counts = failed_df.groupby("ip_address").size()
    for ip, count in fail_counts.items():
        if count >= 5:
            alerts.append({
                "title": "Multiple Failed Login Attempts",
                "body": f"{count} failed login attempts from IP {ip}",
                "icon": "bi bi-shield-lock-fill",
                "ts": "just now",
            })

    # suspicious country login (if VPN mode is OFF)
    if not vpn_mode:
        for _, row in df.iterrows():
            ip = row["ip_address"]
            country = resolve_country(ip)
            if country != allowed_country and country != "Unknown":
                alerts.append({
                    "title": "Suspicious Country Login",
                    "body": f"Login from {country} (IP {ip}) outside expected region",
                    "icon": "bi bi-exclamation-triangle-fill",
                    "ts": row["timestamp"].strftime("%Y-%m-%d %H:%M"),
                })

    # same IP failing across multiple users
    multi_user_fails = failed_df.groupby("ip_address")["uid"].nunique()
    for ip, uid_count in multi_user_fails.items():
        if uid_count >= 3:
            alerts.append({
                "title": "Credential Stuffing Suspected",
                "body": f"{uid_count} different users had failed logins from IP {ip}",
                "icon": "bi bi-person-x-fill",
                "ts": "just now",
            })

    return alerts[:limit]
