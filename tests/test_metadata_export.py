from pprint import pprint

from metadata.master_site import MASTER_SITE


def main():
    pprint(MASTER_SITE.export_for_ai())

    print()
    print(MASTER_SITE.find_value_alias("jenis_battery", "aki"))
    print(MASTER_SITE.find_value_alias("jenis_battery", "VRLA"))
    print(MASTER_SITE.find_value_alias("jenis_battery", "li-ion"))
    print(MASTER_SITE.find_value_alias("jenis_battery", "Lithium"))


if __name__ == "__main__":
    main()