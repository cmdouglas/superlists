#!/bin/sh
script_path="`readlink -f $0`";
script_dir="$(dirname $script_path)";

hostname="$(basename $(dirname $(dirname $script_dir)))";

sed "s/SITENAME/$hostname/g" "$script_dir/nginx.template.conf" \
    | sudo tee "/etc/nginx/sites-available/$hostname";

sudo ln -s "/etc/nginx/sites-available/$hostname" /etc/nginx/sites-enabled/;

sed "s/SITENAME/$hostname/g" "$script_dir/gunicorn-upstart.template.conf" \
    | sudo tee "/etc/init/gunicorn-${hostname}.conf";

sudo service nginx reload;
sudo start "gunicorn-$hostname";
