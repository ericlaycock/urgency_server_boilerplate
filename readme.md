#Setup

1. Initialize a RunPod server.
2. Select this template: RunPod Pytorch 2.2.0https://www.runpod.io/console/explore/runpod-torch-v220
3. Edit the template to use this Container Startup Command:

bash -c "apt update; \
         apt install -y wget portaudio19-dev build-essential; \
         DEBIAN_FRONTEND=noninteractive apt-get install -y openssh-server; \
         mkdir -p ~/.ssh; cd ~/.ssh; chmod 700 ~/.ssh; \
         echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCvEgj9tjpHe/eurdnnc9Z/yyBpHsDMLCrnhn6wCclTokBVaLQvqJnzi8E0Fz+TfMASCoQ3jnoeRR5DfBKahtKb2Kc+7zfh86BLnHaaLXGiTJKjW/XRx1ipy7kIfAxrCk62Ra74h7sLdKLLxmqbZ98yf4AoHPXEGP3WEbmVENEX7E2GCJ10j6GlBP0nM6L6+1Z/tmdvQldf25hdWcqrgiWGQSjDWAFlsFJtN8FTJR2pADs5dEdROoBRuAu/VY+ST4S4+2+OMBu6EdJXsuvsr1vaqY6CcDF0Fe7sKDm+rMrnydbtnA6Ic+DViaJ9dsmJg3ITGqGYygFfxAo6sImh4CVcyrzG2N8IyYUkBTMCIbDtCszJaAxYi9/bl5CJ/jdFoVvPRZpZDlx5l7+40GO9OpHao0soKgfNZAyU9f372yqpJZJdOW3CexEuGp/35l03iHft2vKQdiy+A7+/BGCGBNTjDx5Hoei1dp7vel2W9qOmf0ikTKk1GC2V4A/y+loQH145jHQNfPFnFk9rrg6ToWn1vaYbpA8N34Bv0C9H11I62FI16cp/C47fv6AQES3Vk1kLqQy0RGlrONfMAlFIGhyzC8Bdhcb3Vbf4SesrB6+BW7rpFQdvxUQ14Y00EvS3YaaLcwnXRtnMTOv6rFGESScs12htCQH4OS1cGRgaED5fPQ== ericlaycock44@gmail.com' > authorized_keys; \
         chmod 600 authorized_keys; \
         service ssh start; \
         sleep infinity"


4. Add Port 4000 to the container's ports.

5. Launch RunPod instance. When it's ready, click CONNECT and copy/select the bottommost ssh option.Change the private key to id_rsa instead of id_256 or whatever it is. 

6. In VSCode, open Remote SSH and add new host. Paste that modified command in.

7. Once logged in, run `python app.py` to start the server. (If necessary, run `pip install -r requirements.txt` first.)