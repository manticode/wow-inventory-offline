import argparse
import re
from slpp import slpp as lua


def prerun():
    """ Check input args are valid. """
    argparser = argparse.ArgumentParser(description="Inventory database file.")
    argparser.add_argument("-i", help="the lua datafile", dest="infilename")
    argparser.print_help()
    args = argparser.parse_args()
    luafile = open(args.infilename, "r")
    return luafile


def parse_lua(luadb, toon_name, realm_name):
    """ Parse the lua data"""
    print("parsing...")
    gu_toon_name = toon_name + " - " + realm_name
    inventorydata = luadb.read()
    inventorydataparsed = lua.decode(inventorydata)
    print(inventorydataparsed)
    itemid_list, itemname_list = iter_luadb(inventorydataparsed, toon_name, realm_name)
    get_item_qty(inventorydataparsed, gu_toon_name, itemid_list)
    return itemid_list, itemname_list, qty_list


def extract_item_name(item_string):
    item_name = re.search("^.*\[([a-zA-Z0-9\s\:]*)\].*$", item_string)
    if item_name:
        return item_name.group(1)


def get_item_qty(lua_obj, gu_toon_name, item_id_list, ):
    """ Correlate quantities for respective items."""
    """ TO DO - invert the container lookup to be inside the itemid list lookup otherwise it fails. """
    bank_inv_qty_lookup = lua_obj["AskMrRobotDbClassic"]["char"][gu_toon_name]["BankItemsAndCounts"]
    storage_list_qty = []
    print("performing qty lookup")
    for container_id in bank_inv_qty_lookup:
        print(container_id)
        bank_container = bank_inv_qty_lookup[container_id]
        print("container: ", bank_container)
        print(bank_container)
        for item_id_lookup in item_id_list:
            print("looking up:", item_id_lookup)
            item_qty = bank_container.get(item_id_lookup)
            if item_qty:
                print("item_qty: ", item_qty)
                print("item id: ", item_id_lookup, " .. qty: ", item_qty)
                storage_list_qty.append(item_qty)
            else:
                print("moving onto next container")
                break
        print("item_id_list complete")
    print("bank_inv_qty_lookup complete")
    print(storage_list_qty)

def iter_luadb(lua_obj, toon_name, realm_name):
    """ Extract the stuff we want. Each bag """
    gu_char_name = toon_name + " - " + realm_name
    print("WoW Unique name: ", gu_char_name)
    bank_inv_lookup = lua_obj["AskMrRobotDbClassic"]["char"][gu_char_name]["BankItems"]
    storage_list_itemid = []
    storage_list_itemname = []
    for key in bank_inv_lookup:
        print("bag id: ", key)
        print("contents of bag: ", bank_inv_lookup[key])
        print("type: ", type(bank_inv_lookup[key]))
        bank_container = bank_inv_lookup[key]
        for slot_item in bank_container:
            if slot_item["id"] in storage_list_itemid:
                pass
            else:
                storage_list_itemid.append(slot_item["id"])
                storage_list_itemname.append(extract_item_name(slot_item["link"]))
            print("slot item: ", slot_item["id"], "....", slot_item["link"])

        if isinstance(bank_inv_lookup[key], dict):
            iter_luadb(bank_inv_lookup[key], toon_name, realm_name)
    print(storage_list_itemid)
    print(storage_list_itemname)
    return storage_list_itemid, storage_list_itemname


def main():
    """ Run main part of script. """
    print("main func")
    inv_dict = {}


if __name__ == "__main__":
    toon = "Bankotar"
    realm = "Hydraxian Waterlords"
    print("preparing")
    databaseobj = prerun()
    parse_lua(databaseobj, toon, realm)
    main()
