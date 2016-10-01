
git_config_check() {
	# skip if env vars are set
	if [ -n "$GIT_AUTHOR_NAME" -a -n "$GIT_AUTHOR_EMAIL" ]; then
		return
	fi

	# check if configured in ~/.gitconfig
	email=$(git config --global --get user.email)
	username=$(git config --global --get user.name)

	# it's important for each user have their own ~/.gitconfig
	if [ "$HOME" = "/root" ]; then
		cat >&2 <<-'EOF'

		IMPORTANT: Use 'sudo -s' to become root, so that the $HOME belongs to you not /root

		EOF
	fi

	if [ -n "$email" -a -n "$username" ]; then
		return
	fi

	user=${SUDO_USER:-$(id -un)}
	gecos=$(getent passwd $user | cut -d: -f5)
	email=$user@pld-linux.org

	cat >&2 <<-EOF

	Please commit your changes if you modify any files in /etc to git!
	But before that please setup env vars to identify your commits in your ~/.bash_profile:

	export GIT_AUTHOR_NAME='$gecos'
	export GIT_AUTHOR_EMAIL='$email'

	export GIT_COMMITTER_NAME=\${GIT_COMMITTER_NAME:-\$GIT_AUTHOR_NAME}
	export GIT_COMMITTER_EMAIL=\${GIT_COMMITTER_EMAIL:-\$GIT_AUTHOR_EMAIL}

	NOTE: GIT_* vars are imported with sshd so you could setup them where you connect from.

	You may also use git config, but then you must learn to use 'sudo -s' to become root:
	git config --global user.email '$email'
	git config --global user.name '$gecos'

EOF
}

# run in subshell not to leak variables
git_config_check | cat
unset -f git_config_check
