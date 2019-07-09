import json
from fastecdsa import curve
from fastecdsa import point
import hashlib as hs
import keystorage
import re
import merkle

CURVES = {"secp256k1": curve.secp256k1, "secp224k1": curve.secp224k1, "brainpoolP256r1": curve.brainpoolP256r1,
              "brainpoolP384r1": curve.brainpoolP384r1, "brainpoolP512r1": curve.brainpoolP512r1}

HASH = {str(hs.sha256): hs.sha256, str(hs.sha384): hs.sha384, str(hs.sha512): hs.sha512, str(hs.blake2b): hs.blake2b, str(hs.blake2s): hs.blake2s,
        str(hs.sha3_224): hs.sha3_224, str(hs.sha3_256): hs.sha3_256, str(hs.sha3_384): hs.sha3_384, str(hs.sha3_512): hs.sha3_512,
        str(hs.shake_128): hs.shake_128, str(hs.shake_256): hs.shake_256}

def point_from_str(input):
    """
    Cria um objeto ponto (de uma curva elíptica) a partir de uma string (formatada especficamente) que descreve um
     ponto de uma curva elíptica.
     É utilizado regex para a separação de parâmetros na string.

    :param input: string na forma "X: 'valor da coordenada x em hexadecimal'\nY: 'valor da coordenada y em hexadecimal'\n(On curve <'nome da curva'>)"
    :return: ponto da curva elíptica point.Point(x,y,curve)
    """
    x_value = re.search('X:(.*)\\nY:', input).group(1).strip(' ')
    y_value = re.search('Y:(.*)\\n\\(', input).group(1).strip(' ')
    curve_name = re.search('<(.*)>', input).group(1).strip(' ')

    return point.Point(int(x_value, 0), int(y_value, 0), CURVES[curve_name])


def str_to_proof(input):
    pass


def signature_output(filename, r_point, signature, message, aggregated_key, proof, ec, h_sig, h_tree):
    output = {
        "data_type": 1,
        "r_point": str(r_point),
        "signature": str(signature),
        "message": message,
        "aggregated_key": str(aggregated_key),
        "proof": proof,
        "ec": str(ec),
        "h_sig": str(h_sig),
        "h_tree": str(h_tree)
    }

    with open(filename, 'w') as json_file:
        json.dump(output, json_file)

class Info:
    """
    Classe contendo as informações utilizadas na GUI
    data_type define o tipo do arquivo que irá ser utilizado
    """
    def __init__(self, filepath):
        self.data_code = {"0": self.parse_musig, "1": self.parse_musig_ver, "2": self.parse_root}

        with open(filepath, "r") as read_file:
            data = json.load(read_file)

        self.data_type = data["data_type"]

        self.hostname = None
        self.port = None
        self.my_key = None
        self.message = None

        self.public_key_list = None
        self.address_dict = None
        self.complete_pub_key_lst = None

        self.restrictions = None

        self.ec = curve.secp256k1
        self.h_com = hs.sha256
        self.h_agg = hs.sha256
        self.h_sig = hs.sha256
        self.h_tree = hs.sha256

        self.r_point = None
        self.signature = None
        self.aggregated_key = None
        self.proof = None

        self.root = None

        self.data_code[str(self.data_type)](data)

    def parse_musig(self, data):
        print("Here")
        self.hostname = data["hostname"]
        self.port = data["port"]
        self.my_key = keystorage.import_keys(data["my_key_dir"])
        self.message = data["message"]

        self.public_key_list = []
        self.address_dict = {}
        self.complete_pub_key_lst = []
        self.complete_pub_key_lst.append(self.my_key[1])

        for i in range(data["n_co_signers"]):
            co_signer = data["co_signers"][i]
            pub_key = keystorage.import_keys(co_signer["key_dir"])[1]
            hostname = co_signer["hostname"]
            port = co_signer["port"]
            self.public_key_list.append(pub_key)
            self.complete_pub_key_lst.append(pub_key)
            self.address_dict[str(pub_key)] = (hostname, port)

        for i in range(data["complete_pub_key_number"]):
            key_dir = data["complete_pub_key_lst"][i]
            pub_key = keystorage.import_keys(key_dir)[1]
            self.complete_pub_key_lst.append(pub_key)

        if data["restrictions_number"] > 0:
            self.restrictions = []
            for i in range(data["restrictions_number"]):
                restriction_info = data["restrictions"][i]
                restriction_info_len = len(restriction_info)
                temp_restriction = []
                for j in range(restriction_info_len):
                    key = keystorage.import_keys(restriction_info[j])[1]
                    temp_restriction.append(key)
                self.restrictions.append(tuple(temp_restriction))

        if data["ec"] != "":
            self.ec = CURVES[data["ec"]]

        if data["h_com"] != "":
            self.h_com = HASH[data["h_com"]]

        if data["h_agg"] != "":
            self.h_agg = HASH[data["h_agg"]]

        if data["h_sig"] != "":
            self.h_sig = HASH[data["h_sig"]]

        if data["h_tree"] != "":
            self.h_tree = HASH[data["h_tree"]]

    def parse_musig_ver(self, data):
        self.r_point = point_from_str(data["r_point"])
        self.signature = int(data["signature"])
        self.message = data["message"]
        self.aggregated_key = point_from_str(data["aggregated_key"])
        self.proof = data["proof"]

        if data["ec"] != "":
            self.ec = CURVES[data["ec"]]

        if data["h_sig"] != "":
            self.h_sig = HASH[data["h_sig"]]

        if data["h_tree"] != "":
            self.h_tree = HASH[data["h_tree"]]

    def parse_root(self,data):
        if data["root"] == "":

            self.complete_pub_key_lst = []
            for i in range(data["complete_pub_key_number"]):
                key_dir = data["complete_pub_key_lst"][i]
                pub_key = keystorage.import_keys(key_dir)[1]
                self.complete_pub_key_lst.append(pub_key)

            if data["restrictions_number"] > 0:
                self.restrictions = []
                for i in range(data["restrictions_number"]):
                    restriction_info = data["restrictions"][i]
                    restriction_info_len = len(restriction_info)
                    temp_restriction = []
                    for j in range(restriction_info_len):
                        key = keystorage.import_keys(restriction_info[j])[1]
                        temp_restriction.append(key)
                    self.restrictions.append(tuple(temp_restriction))

            self.root = str(merkle.build_merkle_tree(self.complete_pub_key_lst, self.restrictions)[0])
        else:
            self.root = data["root"]

        if data["h_tree"] != "":
            self.h_tree = HASH[data["h_tree"]]




    def print_test(self):
        print(f'DATA TYPE:{self.data_type}')

        print(f'HOSTNAME: {self.hostname}')
        print(f'PORT: {self.port}')
        print(f'MY KEY: {self.my_key}')
        print(f'MESSAGE: {self.message}')

        print(f'PK LIST: {self.public_key_list}')
        print(f'ADDR DICT: {self.address_dict}')
        print(f'COMPLETE PK LIST: {self.complete_pub_key_lst}')

        print(f'RESTRICTIONS: {self.restrictions}')

        print(f'EC: {self.ec}')
        print(f'COM: {self.h_com}')
        print(f'AGG: {self.h_agg}')
        print(f'SIG: {self.h_sig}')
        print(f'TREE: {self.h_tree}')

        print(f'R POINT: {self.r_point}')
        print(f'SIG: {self.signature}')
        print(f'AGG KEY: {self.aggregated_key}')
        print(f'PROOF: {self.proof}')

        print(f'ROOT: {self.root}')


def main():
    test = Info('teste_root.json')
    test.print_test()


if __name__ == "__main__":
    main()