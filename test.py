#   print(crypto.create_hash("124"))
    print(type(crypto.load_key(crypto.TEST_PUBLIC_KEY,public=True)))
    # print(type(crypto.load_key(crypto.TEST_PRIVATE_KEY,public=False)))
    public_key = crypto.load_key(crypto.TEST_PUBLIC_KEY,public=True)
    private_key = crypto.load_key(crypto.TEST_PRIVATE_KEY,public=False)

    data = bytes([1,2,3,4])
    signature =  crypto.sign(private_key,data)
    print("signature " + str(signature.hex()))
    decimal_string = ",".join(str(byte) for byte in signature)
    print(decimal_string)
    crypto.verify(public_key,data,signature)



    # oslp.protobuf_ver()
    # oslp.message()
    # start_server()
    # oslp.process_request(oslp_msg.registerDeviceRequestData)
    OSLitaP = oslp.oslpservice()