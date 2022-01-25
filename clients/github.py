import requests
import jwt
import time
from github3 import GitHub

github = GitHub()
auth_details = []
all_orgs = ["name1", "name2"]
github_base_url = 'https://api.github.com'

class GithubClient(object):
    def __init__(self):
        app_id = "xxx"

        fname = 'private-key.pem'
        cert_str = open(fname, 'r').read()
        cert_bytes = cert_str.encode()
        pemfile = open(fname, 'r')
        private_key = pemfile.read()
        pemfile.close()

        time_since_epoch_in_seconds = int(time.time())

        payload = {
            'iat': time_since_epoch_in_seconds,
            'exp': time_since_epoch_in_seconds + (10 * 60),
            'iss': app_id
        }

        actual_jwt = jwt.encode(payload, private_key, algorithm='RS256')

        headers = {"Authorization": "Bearer {}".format(actual_jwt.decode()),
                   "Accept": "application/vnd.github.machine-man-preview+json"}

        for org in all_orgs:
            try:
                github.login_as_app(
                    cert_bytes,
                    app_id,
                    600
                )

                installation_id = github.app_installation_for_organization(org).id

                resp = requests.post(f'https://api.github.com/app/installations/{installation_id}/access_tokens',
                                     headers=headers)

                token = resp.json()["token"]

                details ={
                    "org": org,
                    "installation_id": installation_id,
                    "token": token
                }

                auth_details.append(details)

            except:
                print(f"Error with {org}")
                pass


    def get_user(self, id):
        try:
            response = requests.request(
                "GET",
                f"{github_base_url}/user/{id}",
                headers={'Authorization': 'token ' + auth_details[0]["token"]}
            )
        except HttpError as e:
            if e.resp.status in [400, 404]:
                print(f"Error: {e.resp.status}")
            else:
                print("GitHub Error: Bad Response from GitHub API.")
            return 0

        return response.json()

    def remove_member_from_org(self, username, org):

        for each_org in auth_details:
            if each_org['org'] == org:
                response = requests.request(
                    "delete",
                    f"{github_base_url}/orgs/{each_org['org']}/members/{username}",
                    headers={'Authorization': 'token ' + each_org["token"]}
                )

                if response.status_code == 204:
                    return f"Successfully removed {github_base_url}/orgs/{each_org['org']}/members/{username}"
                return f"Failed to remove {github_base_url}/orgs/{each_org['org']}/members/{username}"

    def checkOrgMembership(self, username):
        membership = []
        for each_org in auth_details:
            response = requests.request(
                "GET",
                f"{github_base_url}/orgs/{each_org['org']}/members/{username}",
                headers={'Authorization': 'token ' + each_org["token"]}
            )
            if response.status_code == 204:
                membership.append(each_org['org'])

        return membership

