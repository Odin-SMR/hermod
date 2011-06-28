/**********************************************************
 * This program reads a directory for GRIB files.         *
 *                                                        *
 *                                                        *
 * Functions: Uses buildin functions from stdlib and      *
 *            dirent library as well NETCDF, and          *
 *            GRIBEX library.                             *
 *                                                        *
 * See gribread.h for specifics                           *
 *                                                        *
 *********************************************************/
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <errno.h>
#include <ctype.h>
#include <stdarg.h>
#include <assert.h>
#include <unistd.h>
#include <math.h>
#include <netcdf.h>

#define PRX "ODIN_NWP_"
#define PACKED_TYPE 16

int DEBUG = 0;
int DEBUGXTRA = 0;

// Macros
#define ERRCODE 2
#define ERR(e) {printf("Error: %s\n", nc_strerror(e)); exit(ERRCODE);}
#define NRERROR(error_text) {fprintf(stderr,"ERROR: %s in %s at %d\n",error_text,__FILE__,__LINE__); \
                             exit(EXIT_FAILURE);}
#define CALLOCF(x,y) {x = (float *)calloc(y,sizeof(float)); if(x == NULL) {NRERROR("F memory allocation failed!\n");}}
#define CALLOCD(x,y) {x = (double *)calloc(y,sizeof(double)); if(x == NULL) {NRERROR("D memory allocation failed!\n");}}
#define CALLOCL(x,y) {x = (long *)calloc(y,sizeof(long)); if(x == NULL) {NRERROR("L memory allocation failed!\n");}}
#define CALLOCI(x,y) {x = (int *)calloc(y,sizeof(int)); if(x == NULL) {NRERROR("I memory allocation failed!\n");}}
#define CALLOCS(x,y) {x = (short *)calloc(y,sizeof(short)); if(x == NULL) {NRERROR("SI memory allocation failed!\n");}}
#define stop {fprintf(stderr,"DEBUGGING STOP: %s at %d\n",__FILE__,__LINE__); exit(EXIT_FAILURE);}

#define oops(s) perror((s))
#define MALLOC(s,t) {if(((s) = malloc(t)) == NULL) { oops("error: malloc() "); stop; }}

#define REFPRES   100000.0 // Pascal
#define G0        9.80665   // m s-2 mean g at the equator
#define EQRAD     6378.14e3 // meters
#define FLAT      1.0/298.257
#define Boltzmann 1.380658e-23
#define Avogadro  6.0221367e23
#define UnGascon  Boltzmann * Avogadro
#define Md        28.964
#define Mv        18.016
#define RD        1000.0 * UnGascon/Md
#define RV        1000.0 * UnGascon/Mv
#define CPD       3.5 * RD
#define CVD       CPD - RD
#define CPV       4.0 * RV 
#define KAPPA     287.06/1004.71
#define OMEGA     (2*M_PI)/86164.09053 

#define NVARS 18 // Number of variables in NWP infile
#define MISSING -999.0

typedef struct {
  double scale_factor;
  double add_offset;
  short *sarray;
  float *farray;
} data;

typedef struct {
  char infile[NC_MAX_NAME+1];
  char outfile[NC_MAX_NAME+1];
  int oncid;
  int incid;
  int d3grp;
  int glgrp;
  int d2grp;
  size_t ilev;
  size_t nlon;
  size_t nlat;
  size_t nlev;
  size_t size;
  size_t isize;
  size_t gridsize;
  float *lat;
  float *lon;
  int *nlevs;
  double *A;
  double *B;
  int lvlid;
  int lonid;
  int latid;
  int Tid;
  int Qid;
  int Uid;
  int Vid;
  int VOid;
  int O3id;
  int Pid;
  int CIWCid;
  int CLWCid;
  int GMHid;
  int PVid;
  int PTid;
  int GPid;
  int T2Mid;
  int U10Mid;
  int V10Mid;
  int SKTid;
  int SPid;
  int TCO3id;
  int TCWid;
  int TCWVid;
  int Zid;
  int MSLid;
} GL;

enum VARS {lvl,lon,lat,T,Q,U,V,VO,O3,P,CIWC,CLWC,GMH,PV,PT,GP,T2M,U10M,V10M,SKT,SP,TCO3,TCW,TCWV,Z};

static void USAGE(int nargs,char **args);
static void GetGLInfo(GL *g);
static data *Pack(float *array, size_t size, int p);
static float *Getdata(int ncid, long size, char *vname);
static float *HGP(float *Z, GL *g);
static float *PH(float *SP, GL *g);
static void FullPresGpPt(GL *g, 
			  float *t, 
			  float *q, 
			  float *z, 
			  float *sp,
			  float *vo);
static void GMHPV(GL *g, 
                  float *VO,
                  float *P, 
                  float *PT,
                  float *GP);
static float GeoidRadius(float lat);
static void MaxMin(float *array, long size);
static void MaxMinS(short *array, long size);
static float GRAV(float lat, float z);
static void WriteXtra(char *name, int id, GL *g, long size, int ndim, int p);
static void SetupNC(GL *g);
static void check_err(const int stat, const int line, const char *file);
static void WRITEMD(void *sar, char *type, int varid, int ncid);
static void WRITE1D(void *sar, char *type, int varid, int ncid); 
static void AddAtt(data *Var, int id, int root_grp, char *name, GL *g);
static void handle_error(int status, int line, char *file);
static void remove_extra(char *str, char *str2);
static char *tolowercase(char *vname);
static char *touppercase(char *vname);


