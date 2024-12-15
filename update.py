import glob
import http.client
import json
import os
import shutil
import tempfile
import urllib.parse
import zipfile
from dataclasses import dataclass
from typing import Optional


@dataclass
class Version:
    version: int
    repo: str
    branch: str


@dataclass
class Response:
    status: int
    reason: str
    content: bytes


def request_get(url: str) -> Response:
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path

    conn = http.client.HTTPSConnection(host)
    conn.request("GET", path)

    response = conn.getresponse()
    response_obj = Response(response.status, response.reason, response.read())

    conn.close()
    return response_obj


def get_local_version() -> Version:
    with open("version.json", "r") as version_file:
        data = version_file.read()

    json_data: dict = json.loads(data)
    return Version(json_data["version"], json_data["repo"], json_data["branch"])


def get_remote_version(ver: Version) -> Optional[Version]:
    response = request_get(
        f"https://raw.githubusercontent.com/{ver.repo}/refs/heads/{ver.branch}/version.json"
    )

    if response.status != 200:
        print(f"Failed to fetch version: {response.reason}")
        return None

    json_data: dict = json.loads(response.content)
    return Version(json_data["version"], json_data["repo"], json_data["branch"])


def get_update(ver: Version):
    response = request_get(
        f"https://codeload.github.com/{ver.repo}/zip/refs/heads/{ver.branch}"
    )

    if response.status != 200:
        print(f"Failed to download update: {response.reason}")
        return

    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(response.content)

        with zipfile.ZipFile(temp_file, "r") as zip_ref:
            extract_path = tempfile.mkdtemp()
            zip_ref.extractall(extract_path)

    for item in glob.glob("*", recursive=True):
        if os.path.isfile(item):
            os.remove(item)
        else:
            shutil.rmtree(item)

    folder_name = f"{ver.repo.split("/")[1]}-{ver.branch}"
    extracted_folder = os.path.join(extract_path, folder_name)

    for root, _, files in os.walk(extracted_folder):
        for file in files:
            src_file = os.path.join(root, file)
            relative_path = os.path.relpath(src_file, extracted_folder)
            dest_file = os.path.abspath(relative_path)

            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.move(src_file, dest_file)

    shutil.rmtree(extract_path)
    print("Updated!")


def main():
    local_version = get_local_version()
    if local_version.version is None:
        print("Updates disabled.")
        return

    remote_version = get_remote_version(local_version)
    if remote_version is None:
        return

    if remote_version.version == local_version.version:
        print("No updates!")
        return

    get_update(remote_version)


if __name__ == "__main__":
    main()
