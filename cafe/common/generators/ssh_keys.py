import os
from Crypto.PublicKey import RSA


def generate_rsa_ssh_keys(keyfilename,
                          keyfilepath,
                          key_size=1024,
                          pass_phrase=""):

    if os.path.isfile("{0}/{1}".format(
                      keyfilepath, keyfilename)):
        os.remove("{0}/{1}".format(keyfilepath, keyfilename))
    if os.path.isfile("{0}/{1}.pub".format(keyfilepath, keyfilename)):
        os.remove("{0}/{1}.pub".format(keyfilepath, keyfilename))
    private_key = RSA.generate(key_size)
    public_key = private_key.publickey()
    public_key_file = open("{0}/{1}.pub".format(keyfilepath, keyfilename), "w")
    private_key_file = open("{0}/{1}".format(keyfilepath, keyfilename), "w")
    public_key_file.write(public_key.exportKey(passphrase=pass_phrase))
    private_key_file.write(private_key.exportKey(passphrase=pass_phrase))
    public_key_file.close()
    private_key_file.close()
    if not os.path.isfile("{0}/{1}".format(keyfilepath, keyfilename)):
        return False, "No private key file found"
    if not os.path.isfile("{0}/{1}.pub".format(keyfilepath, keyfilename)):
        return False, "No public key file found"
    return True, ""
