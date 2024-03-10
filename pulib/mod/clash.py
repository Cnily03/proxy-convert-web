from pulib.utils import unique_list


class ClashMod:

    class rules:
        def local(yaml_obj):
            inject_rules = [
                "DOMAIN-SUFFIX,lan,DIRECT",
            ]
            yaml_obj["rules"] = unique_list(inject_rules + yaml_obj["rules"])
