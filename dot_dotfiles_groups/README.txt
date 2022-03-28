This is a workaround for how I want to structure my dotfiles repo.

I want the scripts and symlinked files grouped by folder. 

For example, ./vscode has settings and script files together.

With chezmoi:
1. If I ignore the folder the scripts don't run. 
2. If I ignore just the symlinked files an empty folder is created.

To work around this I put them all in a `.dotfiles_groups` folder.

This gets created in my `HOME` dir but can be ignored by everything. 

Now my files and scripts can live together and I don't have to worry
about updating my `.chezmoiignore` file.