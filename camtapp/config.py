from dataclasses import dataclass


@dataclass
class endpoints:
    report_endpoint: str = "camtrepo"
    settings_endpoint: str = "camtsettings"
    statement_endpoint: str = "camtstatement"
    

