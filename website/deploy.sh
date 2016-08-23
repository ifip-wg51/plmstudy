#!/bin/sh

scp -i ../plmlab.key -r * ubuntu@86.119.37.246:/var/www/plmapi/plmstudy
scp -i ../plmlab.key * ubuntu@86.119.37.246:/var/www/plmapi/
