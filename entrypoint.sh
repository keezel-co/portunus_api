#!/bin/sh

# Create DB Part

CMD_CREATE_DB="python3 /wgpt/create_database.py"
CMD_UWSGI="uwsgi --uid wgpt --gid wgpt --enable-threads --master -s 0.0.0.0:3031 --manage-script-name --mount /=wgpt:app"

if [ -z "$TCP_WAIT" ]
then
    if [ ! -z "$SKIP_CREATE_DB" ] || [ "$SKIP_CREATE_DB" -ne "0" ]
    then
        $CMD_CREATE_DB
    else
        echo Skipping db initialization
    fi
else
    if [ ! -z "$SKIP_CREATE_DB" ] || [ "$SKIP_CREATE_DB" -ne "0" ]
    then
        /wgpt/tcp-wait.sh $TCP_WAIT $CMD_CREATE_DB
    else
        echo Skipping db initialization
    fi

fi

# uWSGI

if [ -z "$TCP_WAIT" ]
then
    $CMD_UWSGI
else
    /wgpt/tcp-wait.sh $TCP_WAIT $CMD_UWSGI
fi
