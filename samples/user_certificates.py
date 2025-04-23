"""
# region client-with-user-certificates
query_string = f"tls=true&userCertFile={path_to_ca_file}&userKeyFile={path_to_key_file}"
connection_string = f"kdb://{username}:{password}@{endpoint}?{query_string}"
client = KurrentDBClient(uri=connection_string)
# endregion client-with-user-certificates
"""
