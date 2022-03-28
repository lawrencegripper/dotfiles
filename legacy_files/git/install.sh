# Disable commit siging in cs as don't have gpg key
if test "$CODESPACES" = "true"
then
  git config commit.gpgsign false
fi