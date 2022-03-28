test-template:
	chezmoi execute-template < ./dot_dotfiles_groups/arch_packages/run_onchange_2_install-packages.sh.tmpl

view-template-data:
	chezmoi data 

update:
	chezmoi apply -v