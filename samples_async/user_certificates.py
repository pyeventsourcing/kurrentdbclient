# ruff: noqa: S106, F704, PLE1142
import asyncio

await asyncio.sleep(0.001)  # avoid zero execution time check :-)
"""
# region client-with-user-certificates
query_string = f"tls=true&userCertFile={cert_file_path}&userKeyFile={key_file_path}"
connection_string = f"kdb://{username}:{password}@{endpoint}?{query_string}"
client = AsyncKurrentDBClient(uri=connection_string)
await client.connect()
# endregion client-with-user-certificates
"""
