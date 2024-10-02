# Setup manully

```
auth      sufficient pam_u2f.so     cue
auth      required  pam_unix.so     try_first_pass nullok
```

in `/etc/pam.d/sudo` and `/etc/pam.d/polkit-1` at the top

Change ownership of the yubikey file so the current user can't add new keys

```
sudo chown root:root /home/lawrencegripper/.config/Yubico/u2f_keys
```

run 

```
pamu2fcfg
```

and check it's in `~/.config/Yubico/u2f_keys`


See: https://support.yubico.com/hc/en-us/articles/360016649099-Ubuntu-Linux-Login-Guide-U2F