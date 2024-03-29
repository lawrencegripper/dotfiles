test-template:
	chezmoi execute-template < dot_dotfiles_groups/1_ubuntu_packages/run_once_1_install-packages.sh.tmpl

test-zsh-template:
	chezmoi execute-template < ./dot_zshrc.tmpl

test-localrc-template:
	chezmoi execute-template < ./dot_localrc.tmpl

view-template-data:
	chezmoi data 

update:
	chezmoi apply -v

test-codespace:
	docker run -it -v ${PWD}:${PWD} \
		--entrypoint /bin/bash \
		-e CODESPACES="true" \
		--workdir ${PWD} \
		ubuntu:20.04 \
		${PWD}/script/bootstrap-ubuntu-curl