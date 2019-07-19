#!/bin/bash
chmod u+xr *.*
start() {
	echo "Starting AlignPlus_SC_JSONGenerator.....";
        HOME_DIR=`pwd`;    
        echo $HOME_DIR
	CLASSPATH=$JAVA_HOME/lib/tools.jar:.;
	for i in `find $HOME_DIR/../lib -name '*.jar' |grep .jar`; do CLASSPATH=$CLASSPATH:$i; done
	CLASSPATH=$CLASSPATH:$HOME_DIR/..;
	echo $CLASSPATH;
	export CLASSPATH;

	uniqueSearchKey="AlignPlus_SC_JSONGenerator."`basename $PWD`;
	nohup java com.merit.tlgapp.services.TLGGrpOrgScoreCardScheduler  $uniqueSearchKey &
	return 0;
}

stop() {
	echo "Stopping AlignPlus_SC_JSONGenerator.....";
	uniqueSearchKey="AlignPlus_SC_JSONGenerator."`basename $PWD`;
	echo $uniqueSearchKey;
	PROCID=`ps xa | grep $uniqueSearchKey  | grep -v grep | sed  "s/^ *//" | cut --fields=1 --delim=" "`;
	echo "AlignPlus_SC_JSONGenerator processID = " $PROCID;
	kill -9 $PROCID;
	return 0;
}

if [ "$1" = "--start" ]; then
	start
elif [ "$1" = "--kill" ]; then
	stop
fi
