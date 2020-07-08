import argparse
import re
import csv
from slpp import slpp as lua


def prerun():
    """ Check input args are valid. """
    argparser = argparse.ArgumentParser(description="Inventory database file.")
    argparser.add_argument("-i", help="the lua datafile", dest="infilename")
    argparser.add_argument("-o", help="Output filename in CSV format", dest="outfilename")
    argparser.add_argument("-n", "--toon_name", help="Character (toon) nam", dest="toon_name")
    argparser.add_argument("-r", "--realm_name", help="Realm (server) name. Defaults to Hydraxian Waterlords if not "
                                                      "specified", dest="realm_name")
    argparser.print_help()
    args = argparser.parse_args()
    luafile = open(args.infilename, "r")
    gu_char_name = get_unique_char_name(args.toon_name, args.realm_name)
    return luafile, gu_char_name


def parse_lua(luadb, gu_toon_name):
    """ Parse the lua data"""
    inventorydata = luadb.read()
    inventorydata = "{ "+inventorydata+" }"
    inventorydataparsed = lua.decode(inventorydata)
    itemid_list, itemname_list = iter_luadb(inventorydataparsed, gu_toon_name)
    qty_list = get_item_qty(inventorydataparsed, gu_toon_name, itemid_list)
    return itemid_list, itemname_list, qty_list


def extract_item_name(item_string):
    item_name = re.search("^.*\[([a-zA-Z0-9\s\:\',\-]*)\].*$", item_string)
    if item_name:
        return item_name.group(1)


def get_item_qty(lua_obj, gu_toon_name, item_id_list):
    """ Correlate quantities for respective items."""
    bank_inv_qty_lookup = lua_obj["AskMrRobotDbClassic"]["char"][gu_toon_name]["BankItemsAndCounts"]
    storage_list_qty = []
    qty_insert = 0
    for item_id_lookup in item_id_list:
        for container_id in bank_inv_qty_lookup:
            bank_container = bank_inv_qty_lookup[container_id]
            item_qty = bank_container.get(item_id_lookup)
            if item_qty:
                qty_insert = qty_insert + item_qty
            else:
                pass
        storage_list_qty.append(qty_insert)
        qty_insert = 0
    return storage_list_qty


def get_unique_char_name(toon_name, realm_name):
    """ globally unique toon name in Name - Realm format"""
    gu_char_name = toon_name + " - " + realm_name
    return gu_char_name


def iter_luadb(lua_obj, gu_char_name):
    """ Extract the stuff we want. Each bag """
    bank_inv_lookup = lua_obj["AskMrRobotDbClassic"]["char"][gu_char_name]["BankItems"]
    storage_list_itemid = []
    storage_list_itemname = []
    for key in bank_inv_lookup:
        bank_container = bank_inv_lookup[key]
        for slot_item in bank_container:
            if slot_item["id"] in storage_list_itemid:
                pass
            else:
                storage_list_itemid.append(slot_item["id"])
                storage_list_itemname.append(extract_item_name(slot_item["link"]))
        if isinstance(bank_inv_lookup[key], dict):
            iter_luadb(bank_inv_lookup[key], toon_name, realm_name)
    return storage_list_itemid, storage_list_itemname


def create_combined_inv(item_id_list, item_name_list, item_qty_list):
    zip_inv = zip(item_name_list, item_qty_list)
    dict_inv = dict(zip_inv)
    return dict_inv


def write_out_csv(inv_dict, outfile):
    with open(outfile, "w") as file_handle:
        writer = csv.writer(file_handle)
        writer.writerows(inv_dict.items())
        file_handle.close()


if __name__ == "__main__":
    databaseobj, gu_name = prerun()
    itemid_list, itemname_list, itemqty_list = parse_lua(databaseobj, gu_name)
    inventory_dict = create_combined_inv(itemid_list, itemname_list, itemqty_list)
    write_out_csv(inventory_dict, "inventory.csv")