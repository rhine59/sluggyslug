# User access and addresses

Updated 15 November 2026. This guide records connection details, not passwords or private keys. See [deployment status](STATUS.md) for what has been verified.

## Web addresses

| Service | Address | Access |
| --- | --- | --- |
| Original public website | https://slugs.granvillehouse.synology.me/ | No login |
| Reorganised website | https://slugs.granvillehouse.synology.me/new/ | No login |
| Visual editor | https://slugs-editor.granvillehouse.synology.me/ | HTTPS and initial account setup confirmed by the owner |
| Synology administration | https://granvillehouse.synology.me:4001/ | NAS administrator login |
| External reports blog | https://slugsreports.blogspot.com/ | Public external website |

## Accounts and credentials

| Account | Username | Authentication and purpose |
| --- | --- | --- |
| NAS administration | `Goredale` | Existing NAS password, held privately by the owner; not an editor login |
| Restricted NAS SSH | `slugs` | Existing SSH private key; internet port **2234**; access confined to the website directory |
| Website editor administrator | Chosen privately by the owner | Initial setup completed; individual username/password held privately; there is no default password |
| Other website editors | Created by an editor administrator | Separate username/password per person; these are independent of NAS accounts |
| GitHub | `rhine59` / repository `sluggyslug` | GitHub account authentication; collaborators need repository access granted by the owner |

Passwords, private SSH keys, setup codes and account databases are deliberately not stored in this repository. Obtain the required secret privately from the owner. Do not use a NAS administrator password as an editor password. The public website itself has no editing login.

## Connect to the NAS using SSH

Host: `granvillehouse.synology.me`  
Port: `2234`  
Username: `slugs`  
Website directory: `/volume1/web/slugs`  
Reorganised website directory: `/volume1/web/slugs/new`

With your approved private key stored locally:

```sh
ssh -p 2234 -i /path/to/your/private-key slugs@granvillehouse.synology.me
```

Verify the server fingerprint with the owner on first connection. The `slugs` account is for website files; it cannot administer NAS containers or certificates. A new person's public key must be authorised before they can connect. Keep private keys on the connecting computer and transfer any necessary credentials privately.

## First editor administrator

The NAS administrator retrieves the private setup code from the running container:

```sh
docker exec slugs-editor cat /data/setup-token
```

After HTTPS is working, open https://slugs-editor.granvillehouse.synology.me/setup, enter the code, and choose an individual username and password of at least 14 characters. Setup closes after the first administrator is created. Never put the code or chosen password into Git or the public website.

## Give someone editing access

1. Sign in to the editor as an administrator and open **User accounts**.
2. Create a separate account for the person and choose the editor role.
3. Set the permitted folder to `new` to limit changes to the reorganised site. A blank permitted folder permits access to the full website root.
4. Share their login privately along with the editor URL and [editing guide](EDITOR.md).
5. Disable their account when access is no longer required.

An editor administrator can reset another user's password through User accounts. For lost NAS or SSH access, contact the NAS owner. Preserve the private `slugs-editor-data` volume: it contains accounts and revision history.

## Operational reference

- Container/project: `slugs-editor`.
- NAS project directory: `/volume1/docker/slugs-editor`.
- Full website mount: `/volume1/web/slugs` → `/site`, read/write.
- Private account/history volume: `slugs-editor-data` → `/data`.
- Internal service: `http://127.0.0.1:8097`, reached through the NAS HTTPS reverse proxy; not a public login address.
- Repository: https://github.com/rhine59/sluggyslug (private).
- Bulk photographs remain on the NAS; see [media restoration instructions](../README.md#rebuild-the-website).
