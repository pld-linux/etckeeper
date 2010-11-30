if [ "$UID" = 0 -a -z "$GIT_AUTHOR_NAME" -a -z "$GIT_AUTHOR_EMAIL" ]; then
	cat <<'EOF'
Please commit your changes if you modify any files in /etc to git!
But before that please setup env vars to identify your commits in your ~/.bash_profile:

export GIT_AUTHOR_NAME='Elan Ruusamäe'
export GIT_AUTHOR_EMAIL='glen@pld-linux.org'

export GIT_COMMITTER_NAME=${GIT_COMMITER_NAME:-$GIT_AUTHOR_NAME}
export GIT_COMMITTER_EMAIL=${GIT_COMMITER_EMAIL:-$GIT_AUTHOR_EMAIL}

 -glen
EOF
fi
