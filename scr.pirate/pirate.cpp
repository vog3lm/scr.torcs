#include <string>
#include <iostream>
#include <fstream>
#include <track.h>

#include "sensors.h"
#include "obstacles.h"

using namespace std;

static FILE *df;
static tTrack *curTrack;
static float prevDist = -1;
static float distRaced = 0;
static int totalLaps = -1;

static Sensors *trackSens[10];
static Sensors *focusSens[10];
static Obstacles *oppSens[10];
static float trackSensAngle[10][19];

/* create datasource dependencies (filebase) */
static void create(tTrack* track){
    curTrack = track;
    printf("NOTE: track information received\n");
}

static void start(int index, tCarElt* car, tSituation *s, string driver){
    printf("NOTE: init focus sensors not implemented\nNOTE: init track sensors not implemented\nNOTE: init opponents sensors not implemented\n");
    /* init focus sensors
    focusSens[index] = new Sensors(car, 5);
    for(int i = 0; i < 5; ++i){
        focusSens[index]->setSensor(i,(car->_focusCmd)+i-2.0,200);
    } */
    /* init track sensors
    trackSens[index] = new Sensors(car, 19);
    for(int i = 0; i < 19; ++i){
        trackSens[index]->setSensor(i,trackSensAngle[index][i],200);
    } */
    /* init opponents sensors */
    //oppSens[index] = new Obstacles(36, curTrack, car, s, 200);
    printf("NOTE: race information received\n");
    /* init data file */
    string head = "time"
       /* sensor value head */
       ";pitch;distFromStart;rpm;angle;trackPos;lap"
       ";distRaced;yaw;damage;curLapTime;fuel;roll;pitch;speedGlobalX;speedGlobalY"
       ";gear;wheelSpinVel;speedX;speedY;speedZ;racePos;lastLapTime;x;y;z"
       // ";track,opponents;focus" // init not implemented
       /* actor value head */
       ";brake;accel;steer;gear;clutch;focus";
    /* filebase dependencies */
    totalLaps = car->_remainingLaps;
    string laps = std::to_string(totalLaps);
    string trackname = curTrack->filename;
    trackname = trackname.substr(7,trackname.size());
    trackname = trackname.substr(trackname.find_first_of('/')+1,trackname.size());
    trackname = trackname.substr(0,trackname.find_first_of('/'));
    string path = "/root/pi.simulation/scr.torcs/scr.data/"+driver+"."+trackname+"."+laps+"-laps.csv";
    printf("INFO: data file path is %s\n",path.c_str());
    /* create file and write head */
    df = fopen(path.c_str(),"w+");
    fprintf(df,"%s\n",head.c_str());


}
/* parse and write sensor values */
/* unused car sensors
    car->_bestLapTime
    car->_timeBehindLeader
    car->_remainingLaps
    car->_lapsBehindLeader
    car->_steerLock
    car->_gearRatio[]
    car->_gearOffset
    car->_enginerpmRedLine
    car->_raceCmd
    car->_fuel
    car->_tank

    car->_dimension_x
    car->_dimension_y
    car->_dimension_z

    car->_focusCD
    car->_curLapTime
    car->_curTime
    car->_carHandle
    
    car->_pitRepair */
/* unused race sensors 

    car->race.laps */
/* unused track sensors
    car->_trkPos.toMiddle
    car->_trkPos.toStart
    car->_trkPos.seg->width
    car->_trkPos.seg->type
    car->_trkPos.seg->length
    car->_trkPos.seg->arc
    car->_trkPos.seg->radius
    car->_trkPos.seg->surface->kFriction
     */
static void capture(int index, tCarElt* car, tSituation *s){
    /* parse wheel spin for all four wheels
       0: 1: 2: 3: */
    string wheelSpinVel = "(";
    for(int i=0; i<4; ++i){
        wheelSpinVel += std::to_string(car->_wheelSpinVel(i))+",";
    }
    wheelSpinVel = wheelSpinVel.substr(0,wheelSpinVel.size()-1)+")";
    /* parse wheel radius for all four wheels (unwritten)
       0: 1: 2: 3: */
    string wheelRadius = "(";
    for(int i=0; i<4; ++i){
        wheelRadius += std::to_string(car->_wheelRadius(i))+",";
    }
    wheelRadius = wheelRadius.substr(0,wheelRadius.size()-1)+")";
    /* calculate angle between car and middle line (normalized)*/
    float angle = RtTrackSideTgAngleL(&(car->_trkPos))-car->_yaw;
    NORM_PI_PI(angle); /* [-PI,+PI] +/
    /* calculate total distance raced */
    if(prevDist<0){
        prevDist = car->race.distFromStartLine;
    }
    float curDistRaced = car->race.distFromStartLine-prevDist;
    prevDist = car->race.distFromStartLine;
    if(curDistRaced>100){
        curDistRaced -= curTrack->length;
    }
    if(curDistRaced<-100){
        curDistRaced += curTrack->length;
    }
    distRaced += curDistRaced;
    /* calculate distance to middle line */
    float dist_to_middle = 2*car->_trkPos.toMiddle/(car->_trkPos.seg->width);
    /* calculate current lap */
    int curLap = totalLaps - car->_remainingLaps;
    /* parse track sensors
    float trackSensorOut[19];
    // string = trackSensorOut = "(";
    float focusSensorOut[5];
    // string = focusSensorOut = "(";
    if(dist_to_middle<=1.0 && dist_to_middle >=-1.0){ // on track
        trackSens[index]->sensors_update(); // major dependency tackSens, init in newRace
        for(int i = 0; i < 19; ++i){
            trackSensorOut[i] = trackSens[index]->getSensorOut(i);
            if(getNoisy()){
                trackSensorOut[i] *= normRand(1,0.1);
            }
        }
        focusSens[index]->sensors_update(); // major dependency tackSens, init in newRace
        if((car->_focusCD <= car->_curLapTime + car->_curTime) && (car->_focusCmd != 360)){
            for(int i = 0; i < 5; ++i){
                focusSensorOut[i] = focusSens[index]->getSensorOut(i);
                if(getNoisy()){
                    focusSensorOut[i] *= normRand(1,0.01);
                }
            }
            car->_focusCD = car->_curLapTime + car->_curTime + 1.0;
        }else{
            for(int i = 0; i < 5; ++i){
                focusSensorOut[i] = -1;
            }
        }
    }else{ // off track
        for(int i = 0; i < 19; ++i){
            // trackSensorOut = "(-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1)"
            trackSensorOut[i] = -1;
        }
        for(int i = 0; i < 5; ++i){
            // focusSensorOut = "(-1,-1,-1,-1,-1,-1)"
            focusSensorOut[i] = -1;
        }
    }
*/
    /* parse opponent sensors
    float oppSensorOut[36];
    // string = oppSensorOut = "(";
    oppSens[index]->sensors_update(s); // major dependency, init in newRace
    for(int i = 0; i < 36; ++i){
        oppSensorOut[i] = oppSens[index]->getObstacleSensorOut(i);
        if (getNoisy())
            oppSensorOut[i] *= normRand(1,0.02);
            // oppSensorOut += (normRand(1,OPP_NOISE_STD))+",";
    }
    //oppSensorOut = oppSensorOut.substr(0,oppSensorOut.size()-1)+")";
*/
    /* create data string */    
    string data = std::to_string(s->currentTime); // timestamp racestart=0
    /* sensor values */
    data += ";"+std::to_string(car->_pitch); // pitch
    data += ";"+std::to_string(car->race.distFromStartLine);
    data += ";"+std::to_string(car->_enginerpm*10);
    data += ";"+std::to_string(angle);
    data += ";"+std::to_string(dist_to_middle);
    data += ";"+std::to_string(curLap);
    data += ";"+std::to_string(distRaced);
    data += ";"+std::to_string(car->_yaw);
    data += ";"+std::to_string(car->_dammage);
    data += ";"+std::to_string(car->_curLapTime);
    data += ";"+std::to_string(car->_fuel);
    data += ";"+std::to_string(car->_roll);
    data += ";"+std::to_string(car->_speed_X);
    data += ";"+std::to_string(car->_speed_Y);
    data += ";"+std::to_string(car->_gear);
    data += ";"+wheelSpinVel;
    data += ";"+std::to_string(car->_speed_x*3.6);
    data += ";"+std::to_string(car->_speed_y*3.6);
    data += ";"+std::to_string(car->_speed_z*3.6);
    data += ";"+std::to_string(car->race.pos);
    data += ";"+std::to_string(car->_lastLapTime);
    data += ";"+std::to_string(car->_pos_X);
    data += ";"+std::to_string(car->_pos_Y);
    data += ";"+std::to_string(car->_pos_Z-RtTrackHeightL(&(car->_trkPos)));
//    data += ";"+trackSensorOut
//    data += ";"+oppSensorOut
//    data += ";" +car->focusSensorOut
    /* actor values */
    data += ";"+std::to_string(car->_brakeCmd);
    data += ";"+std::to_string(car->_accelCmd);
    data += ";"+std::to_string(car->_steerCmd);
    data += ";"+std::to_string(car->_gearCmd);
    data += ";"+std::to_string(car->_clutchCmd);
    data += ";"+std::to_string(car->_focusCmd);
    /* write to file */
    fprintf(df,"%s\n",data.c_str());
}
/* clean it up */
static void kill(int index, tCarElt *car, tSituation *s){
    fclose(df);
}
