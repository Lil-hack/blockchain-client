from bipwallet.utils import *

def gen_address(index):
    # Ваша seed фраза
    seed = 'YOUR SEED'

    # Мастер ключ из seed фразы
    master_key = HDPrivateKey.master_key_from_mnemonic(seed)

    # public_key из мастер ключа по пути 'm/44/0/0/0'
    root_keys = HDKey.from_path(master_key, "m/44'/0'/0'/0")[-1].public_key.to_b58check()

    # Extended public key
    xpublic_key = str(root_keys, encoding="utf-8")

    # Адрес дочернего кошелька в зависимости от значения index
    address = Wallet.deserialize(xpublic_key, network='BTC').get_child(index, is_prime=False).to_address()

    rootkeys_wif = HDKey.from_path(master_key, f"m/44'/0'/0'/0/{index}")[-1]

    # Extended private key
    xprivatekey = str(rootkeys_wif.to_b58check(), encoding="utf-8")

    # Wallet import format
    wif = Wallet.deserialize(xprivatekey, network='BTC').export_to_wif()

    return address, str(wif, 'utf-8')

print(gen_address(0))

