from bipwallet.utils import *

def gen_address(index):
    seed = 'width angry fun govern napkin random chest live metal fuel panic shed'
    master_key = HDPrivateKey.master_key_from_mnemonic(seed)
    root_keys = HDKey.from_path(master_key, "m/44'/0'/0'/0")[-1].public_key.to_b58check()
    xpublic_key = root_keys
    address = Wallet.deserialize(xpublic_key, network='BTC').get_child(index, is_prime=False).to_address()
    rootkeys_wif = HDKey.from_path(master_key, f"m/44'/0'/0'/0/{index}")[-1]
    xprivatekey = rootkeys_wif.to_b58check()
    wif = Wallet.deserialize(xprivatekey, network='BTC').export_to_wif()

    return address, wif

print(gen_address(0))

