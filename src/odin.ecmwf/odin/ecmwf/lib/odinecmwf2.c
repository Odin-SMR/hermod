/*********************************************************
 * This program reads a directory for NETCDF files.      *
 *                                                       *
 *                                                       *
 * Funccreations: Uses buildin functions from stdlib and *
 *            dirent library as well NETCDF, and         *
 *            CDI library.                               *
 *                                                       *
 * See odinecmwf.h for specifics                         *
 *                                                       *
 ********************************************************/
#include "odinecmwf.h"

int main(int argc, char *argv[]) {
  
  int status;
  GL *g = NULL;
  char tname[50], name[50];
  int tid;
  size_t tlen;

  if(argc != 2) {
    USAGE(argc,argv);
    printf("INFO: argc = %d\n",argc);
  }

  g = (GL *)malloc(sizeof(GL));
  if(g == NULL) NRERROR("Failed to allocate mem for geolocation struct");

  strcpy(g->infile,argv[1]);

  printf("INFO: Calling program %s for file %s\n",argv[0],argv[1]);
  
  printf("INFO: Opening file ->%s\n",g->infile);    
  status = nc_open(g->infile, NC_NOWRITE, &g->incid); 
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);

  status = nc_inq_varid (g->incid,"time", &tid);
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  
  // find out how much space is needed for attribute values 
  status = nc_inq_attlen (g->incid,tid, "units", &tlen);
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  status = nc_get_att_text(g->incid,tid, "units", tname);
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  tname[tlen] = '\0';   
  if(DEBUG) printf("%s\n",tname);
  remove_extra(tname,name);
  if(DEBUG) printf("%s\n",name);

  printf("Get the nlat nlon and size for data variables\n");  

  GetGLInfo(g);
  
  //Contruct the output file
  strcpy(g->outfile,PRX);
  strcat(g->outfile,name);
  strcat(g->outfile,"_");
  sprintf(name,"%02ld",g->nlev);
  strcat(g->outfile,name);
  strcat(g->outfile,"_AN.NC");
  printf("Outfile = %s\n",g->outfile);

  printf("Seting up the output file...\n");
  SetupNC(g);

  // Add the time to the file
  status = nc_put_att_text(g->oncid,NC_GLOBAL,"Time",strlen(tname),tname);
  check_err(status,__LINE__,__FILE__);

  float *sp = Getdata(g->incid,(long)g->gridsize,"SP");
  float *z  = Getdata(g->incid,(long)g->gridsize,"Z");
  float *t  = Getdata(g->incid,(long)g->size,"t");
  float *q  = Getdata(g->incid,(long)g->size,"q");
  float *vo = Getdata(g->incid,(long)g->size,"vo");

  printf("INFO MAIN: Calculate and write the full pressure fields, GP, GMH, PT, and PV. Note: half levels are not saved\n");  
  FullPresGpPt(g,t,q,z,sp,vo);
  free(sp); sp = NULL;
  free(z); z = NULL;
  free(q); q = NULL;
  free(vo); vo = NULL;

  WRITE1D(g->lat,"f",g->latid,g->glgrp);
  WRITE1D(g->lon,"f",g->lonid,g->glgrp);
  WRITE1D(g->nlevs,"i",g->lvlid,g->glgrp);    
 
  WriteXtra("T",g->Tid,g,(long)g->size,3,1);
  WriteXtra("Q",g->Qid,g,(long)g->size,3,0);
  WriteXtra("U",g->Uid,g,(long)g->size,3,1);
  WriteXtra("V",g->Vid,g,(long)g->size,3,1);
  WriteXtra("O3",g->O3id,g,(long)g->size,3,0);
  WriteXtra("CIWC",g->CIWCid,g,(long)g->size,3,0);
  WriteXtra("CLWC",g->CLWCid,g,(long)g->size,3,0);
  WriteXtra("T2M",g->T2Mid,g,(long)g->gridsize,2,1);
  WriteXtra("U10M",g->U10Mid,g,(long)g->gridsize,2,1);
  WriteXtra("V10M",g->V10Mid,g,(long)g->gridsize,2,1);
  WriteXtra("TCO3",g->TCO3id,g,(long)g->gridsize,2,1);
  WriteXtra("TCW",g->TCWid,g,(long)g->gridsize,2,1);
  WriteXtra("TCWV",g->TCWVid,g,(long)g->gridsize,2,1);
  WriteXtra("SKT",g->SKTid,g,(long)g->gridsize,2,1);
  WriteXtra("SP",g->SPid,g,(long)g->gridsize,2,1);
  WriteXtra("Z",g->Zid,g,(long)g->gridsize,2,1);
	
  status = nc_close(g->oncid);
  if(status != NC_NOERR) check_err(status,__LINE__,__FILE__);
  status = nc_close(g->incid);
  if(status != NC_NOERR) check_err(status,__LINE__,__FILE__);
  //streamClose(g->streamID);
  if(g) free(g); g = NULL;
  printf("Process complete :-)\n");
 
  return EXIT_SUCCESS;
}

static void remove_extra(char *str, char *str2) {
  int p; 
  int count = 0;
  for(p = 0; p < strlen(str); p++) {
    if(str[p] == 'h' || 
       str[p] == 'o' || 
       str[p] == 'u' || 
       str[p] == 'r' || 
       str[p] == 's' || 
       str[p] == 'i' || 
       str[p] == 'n' || 
       str[p] == 'c' ||
       str[p] == ' ' || 
       str[p] == 'e') {
      continue;
    } else {
      if(str[p] == ':' || str[p] == '-') str2[count++] = '_'; else str2[count++] = str[p];
    }
  }
  str2[count] = '\0';
  return;
}

static void WriteXtra(char *name, int id, GL *g, long size, int ndim, int p) {

  data *m;
  
  float *array = Getdata(g->incid,size,name);
  if(ndim == 3) {
    m = Pack(array,g->size,p);
    free(array); array = NULL;
    AddAtt(m,id,g->d3grp,name,g);
    if(p == 1) {
      WRITEMD(m->sarray,"s",id,g->d3grp);
      free(m->sarray); free(m); m = NULL;
    }
    if(p == 0) {
      WRITEMD(m->farray,"f",id,g->d3grp);
      free(m->farray); free(m); m = NULL;
    }
  } else if(ndim == 2) {
    m = Pack(array,g->gridsize,p);
    free(array); array = NULL;
    AddAtt(m,id,g->d2grp,name,g);
    if(p == 1) {
      WRITEMD(m->sarray,"s",id,g->d2grp);
      free(m->sarray); free(m); m = NULL;
      
    }
    if(p == 0) {
      WRITEMD(m->farray,"f",id,g->d2grp);
      free(m->farray); free(m); m = NULL;
    }
  } else {
    NRERROR("Number of dims not 2 or 3!");
  }  
  return;
}

static float *PH(float *SP, GL *g) {
  
  int i,k;
  printf("INFO PH: Calculating the half pressure PH\n");
  
  long gridsize = (long)g->gridsize;
  long isize = (long)gridsize*g->ilev;
  float *ph;
  if(DEBUG) printf("DEBUG PH: ILEV %d GRIDSIZE = %ld ISIZE = %ld\n",(int)g->ilev,gridsize,isize);

  CALLOCF(ph,isize);

  for (k = (int)g->ilev-1; k > -1; k--) { // Integrate from the ground up. Loop over levels
    long lev = (k)*gridsize;
    for(i = 0; i < gridsize; i++) { 
      ph[lev+i] = g->A[k] + g->B[k] * SP[i]; // first half level is pos 91 = SFC pressure: A= 0 & B = 1 
    }
  }
  MaxMin(ph,isize);
  return ph; 
}

static float *HGP(float *Z, GL *g) {

  int i;
   
  printf("INFO HGP: Setting the elevation to the half GP\n");
  long gridsize = (long)g->gridsize;
  long ground = (long)gridsize*(g->ilev-1);
  long isize = (long)gridsize*g->ilev;

  float *hgp = NULL;
  CALLOCF(hgp,isize);  

  for(i = 0; i < gridsize; i++) hgp[ground+i] = Z[i];  
  MaxMin(hgp,isize);
 
  return hgp; 
}

static float *Getdata(int ncid, long size, char *vname) {
  
  int n, status;
  float *array;
  char *buffer;
 
  printf("Assumes the variables in the file are floats\n");
  status = nc_inq_varid(ncid,buffer=tolowercase(vname),&n); 
  if(status != NC_NOERR) {
    printf("Variable name error. Not lower case! Checking upper case...\n");
    status = nc_inq_varid(ncid,buffer=touppercase(vname),&n);
     if(status != NC_NOERR) {
      printf("Varaible %s not found in file!\n",vname);
      check_err(status,__LINE__,__FILE__);
    } else {
      printf("Variable is found!");
    }
  } else {
    printf("Variable %s is found!",vname);
  }

  CALLOCF(array,size);
  status = nc_get_var_float(ncid,n,array);  
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);

  return array;
}

static void GetGLInfo(GL *g) {
  
  int status = 0, i; 
  size_t len;
  int ncid = g->incid;
  int dimid;
  int varid;

  printf("Extract meta data\n");

  // Get the lon
  status = nc_inq_dimid(ncid,"lon",&dimid);  // get ID for lat dimension
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  status = nc_inq_dimlen(ncid,dimid,&len); // get lon length 
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  g->nlon = len;
  CALLOCF(g->lon,(int)len);
  status = nc_inq_varid(ncid,"lon",&varid);
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  status = nc_get_var_float(ncid,varid,g->lon);
  if(status != NC_NOERR) check_err(status,__LINE__,__FILE__); 

  // Get the lat
  status = nc_inq_dimid(ncid,"lat",&dimid);  
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  status = nc_inq_dimlen(ncid,dimid,&len); 
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  g->nlat = len;
  CALLOCF(g->lat,(int)len);
  status = nc_inq_varid(ncid,"lat",&varid);
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  status = nc_get_var_float(ncid,varid,g->lat);
  if(status != NC_NOERR) 
 
  // Get the levs
  status = nc_inq_dimid(ncid,"mlev",&dimid);  
  if (status != NC_NOERR) check_err(status,__LINE__,__FILE__);  
  status = nc_inq_dimlen(ncid,dimid,&len); 
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  g->nlev = (int)len;
  CALLOCI(g->nlevs,(int)len);
   // Copy data to int array
  //for(i = 0; i < (int)len; i++) g->nlevs[i] = tmp[i];

  // Get intermediate levels
  status = nc_inq_dimid(ncid,"ilev",&dimid);  
  if (status != NC_NOERR) check_err(status,__LINE__,__FILE__); 
  status = nc_inq_dimlen(ncid,dimid,&len); 
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  g->ilev = len;

  // Get the A and B coefficients
  CALLOCD(g->A,(int)g->ilev);
  status = nc_inq_varid(ncid,"hyai",&varid);
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  status = nc_get_var_double(ncid,varid,g->A);
  if(status != NC_NOERR) check_err(status,__LINE__,__FILE__); 
 
  CALLOCD(g->B,(int)g->ilev);
  status = nc_inq_varid(ncid,"hybi",&varid);
  if (status != NC_NOERR) handle_error(status,__LINE__,__FILE__);
  status = nc_get_var_double(ncid,varid,g->B);
  if(status != NC_NOERR) check_err(status,__LINE__,__FILE__); 

  printf("Assigning the data...\n");
  g->gridsize = g->nlon*g->nlat;
  g->size = g->nlev*g->nlat*g->nlon;
  g->isize = g->ilev*g->nlat*g->nlon;
  printf("INFO: NLEV = %d, ILEV = %d, NLON = %d, NLAT = %d, GRIDSIZE = %d, SIZE = %d ISIZE = %d\n", \
	 (int)g->nlev,(int)g->ilev,(int)g->nlon,(int)g->nlat,(int)g->gridsize,(int)g->size,(int)g->isize);

  return;
}
 
//  Program usage
static void USAGE(int nargs,char **args) {
  
  int i = -1;
  
  fprintf(stderr,"ERROR: 1 argument: a netcdf file is accepted\n");
  if (nargs > 2) {
    fprintf(stderr,"ERROR: Number of arguments -> %d\n",nargs);     
    for(i = 0; i < nargs; i++) {
      fprintf(stderr,"ERROR: ARGV[%d] -> %s\n",i,args[i]);     
    }
  }
  NRERROR("Incorrect number of arguments given");
}

static data *Pack(float *array, size_t size, int p) {

  int k;

  data *m = (data *)malloc(sizeof(data));
  if(m == NULL) NRERROR("Couldn't allocate memory for m!");

  if(p == 1) {
    CALLOCS(m->sarray,(int)size);
    m->farray = NULL; 
  
    double min = -999;
    double max = -999;
    
    for(k = 0; k < (long)size; k++) {
      if(round(array[k]) == round(MISSING)) {
	continue;
      } else {
	min = array[k];
	max = array[k];
	break;
      }
    }
    for(k = 0; k < (long)size; k++) {
      if(array[k] < min) min = array[k];
      if(array[k] > max) max = array[k];
    }
    
    m->scale_factor = (max - min)/(pow(2,PACKED_TYPE)-1);
    m->add_offset = min + pow(2,PACKED_TYPE-1) * m->scale_factor;
    
    if(DEBUGXTRA) {
      printf("Min = %f\t Max = %f\n",min, max);
      printf("SHORT: Scale_Factor = %f Add_Offset = %f\n",m->scale_factor,m->add_offset);
    }
    // copy the packed data to output array
    for(k = 0; k < (long)size; k++) m->sarray[k] = lrint((array[k]-m->add_offset)/m->scale_factor);
    
    //Test the arrays
    if(DEBUGXTRA) {
      for(k = 0; k < (long)size; k = k+size/500) {
    	printf("Data = %15.8f\t Packed = %d Unpacked = %15.8f\n",array[k],m->sarray[k],m->sarray[k]*m->scale_factor + m->add_offset);
      }
    }
    if(DEBUG) MaxMinS(m->sarray,(long)size);
  } else if(p == 0) { // if the array is not to be packed
    CALLOCF(m->farray,(long)size);
    m->sarray = NULL; 
    for(k = 0; k < (long)size; k++) m->farray[k] = array[k]; 
    m->scale_factor = 1;
    m->add_offset = 0;
    if(DEBUG) {
      MaxMin(m->farray,(long)size);
      printf("Float: Scale_Factor = %f Add_Offset = %f\n",m->scale_factor,m->add_offset);
    }
  }
  return m;
}

// Calculates the half pressures using the formula: P_level = A_half_level + B_half_level * P_sfc
// You must first calculate the half level before you can calculate the full pressure levels using:
// Pk = 1/2(Pk_+1/2 + Pk_1/2).

static void FullPresGpPt(GL *g, 
			  float *t, 
			  float *q, 
			  float *z, 
			  float *sp,
			  float *vo) {
  
  int i, k; 
  float  fpmax = 0.0, fpmin = 0.0, gpmax = 0.0, gpmin = 0.0;
  float  ptmax = 0.0, ptmin = 0.0;
  float lvl_fpmax = 0, lvl_fpmin = 0, lvl_ptmax = 0, lvl_ptmin = 0;
  float lvl_gpmax = 0, lvl_gpmin = 0;
  long gridsize = g->nlon*g->nlat;
  long size = (long)g->nlon*g->nlat*g->nlev;
  long isize = (long)g->nlon*g->nlat*g->ilev;
  int nlev = (long)g->nlev;
  double logp;
  double dp;
  double alpha;
  
  if(DEBUG) printf("Calculate the half levels: Pressure\n"); 
  float *ph = PH(sp,g);

  if(DEBUG) printf("Calculate the half levels: GP\n"); 
  float *hgp = HGP(z,g);

  float *gp = NULL, *fp = NULL, *pt = NULL;
  printf("Allocate some memory for GP, P, and PT\n");
  CALLOCF(gp,size); 
  CALLOCF(fp,size); 
  CALLOCF(pt,size); 
  
  printf("Calculating the Full pressure, potential temp, and gp\n");

  for (k = nlev-1; k > -1; k--) { // Integrate from the ground up. Loop over levels
    long lev = k*gridsize;   // first level
    long lwrlev = (k+1)*gridsize; // The lower level
    for(i = 0; i < gridsize; i++) { // loop i
      if((lev+i) >= size) NRERROR("lev+i index out of bounds!");
      if((lwrlev+i) >= isize) NRERROR("lwrlev+i index out of bounds!");
    
      double Tv = t[lev+i]*(1 + (RV/RD -1)*q[lev+i]);
     
      if(k == 0) {
	alpha = log(2);
      } else {
	logp  = log(ph[lwrlev+i]/ph[lev+i]);
	dp    = ph[lwrlev+i] - ph[lev+i];
	alpha = 1.0 - ((ph[lev+i]/dp)*logp);
      }
      //printf("logp = %f dp = %f alpha = %f\n",logp,dp,alpha);
      fp[lev+i] = (ph[lev+i] + ph[lwrlev+i])*0.5; // Full pressure level
      gp[lev+i] = hgp[lwrlev+i] + (RD*Tv*alpha);        
      
      //Calculate Potential Temperature without taking into account moisture
      pt[lev+i] = t[lev+i]*pow((REFPRES/fp[lev+i]),KAPPA);    
      // add the next half level
      hgp[lev+i] = hgp[lwrlev+i] + RD*Tv*log(ph[lwrlev+i]/ph[lev+i]);

      if(i == 0) {
	lvl_fpmax  = fp[lev+i];
	lvl_fpmin  = fp[lev+i];
	lvl_ptmax  = pt[lev+i];
	lvl_ptmin  = pt[lev+i];
	lvl_gpmax = gp[lev+i];
	lvl_gpmin = gp[lev+i];
      } else {
	if(fp[lev+i] > lvl_fpmax) lvl_fpmax = fp[lev+i];
	if(fp[lev+i] < lvl_fpmin) lvl_fpmin = fp[lev+i];
	if(pt[lev+i]  > lvl_ptmax) lvl_ptmax = pt[lev+i];
	if(pt[lev+i]  < lvl_ptmin) lvl_ptmin = pt[lev+i];
	if(gp[lev+i] > lvl_gpmax) lvl_gpmax = gp[lev+i];
	if(gp[lev+i] < lvl_gpmin) lvl_gpmin = gp[lev+i];
      }
    } // end for loop for i
    if(k == nlev-1) {
      fpmax  = lvl_fpmax;
      fpmin  = lvl_fpmin;
      ptmax  = lvl_ptmax;
      ptmin  = lvl_ptmin;
      gpmax = lvl_gpmax;
      gpmin = lvl_gpmin;
    } else { 
      if(lvl_ptmax > ptmax) ptmax = lvl_ptmax;
      if(lvl_ptmin < ptmin) ptmin = lvl_ptmin;
      if(lvl_gpmax > gpmax) gpmax = lvl_gpmax;
      if(lvl_gpmin < gpmin) gpmin = lvl_gpmin;
      if(lvl_fpmax > fpmax) fpmax = lvl_fpmax;
      if(lvl_fpmin < fpmin) fpmin = lvl_fpmin;
    }
    if(DEBUG) {
      printf("Level = %03d MaxP = %8.3f MinP = %8.3f Maxgp = %8.3f Mingp = %8.3f MaxPT = %8.3f MinPT = %8.3f\n",k, \
	     lvl_fpmax,lvl_fpmin,lvl_gpmax,lvl_gpmin,lvl_ptmax,lvl_ptmin);
    }  
  } // end loop for k
  printf("Completed loop over all levels. Calculating the scaling factors and add_offsets\n");
   
  // Calculate the geometric height and potential vorticity
   
  // Add the scale_factor and add_offset, write data, and free array
  printf("Calling the function for GMH and PV calculations...\n");
  GMHPV(g,vo,fp,pt,gp);
  printf("Completed calculations...\n");

  data *P   = Pack(fp,size,1);
  data *GP = Pack(gp,size,1);
  data *PT  = Pack(pt,size,1);

  free(fp);   fp = NULL;
  free(gp);  gp  = NULL;
  free(pt);   pt   = NULL;
  free(hgp); hgp = NULL;
  free(ph);   ph   = NULL;

  AddAtt(GP,g->GPid,g->d3grp,"gp",g);
  WRITEMD(GP->sarray,"s",g->GPid,g->d3grp);
  free(GP->sarray); free(GP);
  
  AddAtt(PT,g->PTid,g->d3grp,"PT",g);
  WRITEMD(PT->sarray,"s",g->PTid,g->d3grp);
  free(PT->sarray); free(PT);
  
  AddAtt(P,g->Pid,g->d3grp,"P",g);
  WRITEMD(P->sarray,"s",g->Pid,g->d3grp);
  free(P->sarray); free(P);
  
  return;
}

// Calculates the geometric height and potential vorticity from the relative vorticity
static void GMHPV(GL *g, 
		  float *VO, 
		  float *P,
		  float *PT,
		  float *gp) {
  
  int nlev = (int)g->nlev;
  int i, k, li; 
  float D2R = M_PI/180;	
  double gravity = 0;
  float gm_max = 0.0, gm_min = 0.0, pv_min = 0.0, pv_max = 0.0;
  float lvlgm_max = 0, lvlgm_min = 0, lming = 0, lmaxg = 0;
  float lvlpv_max = 0, lvlpv_min = 0, ming = 0, maxg = 0;
  //double OMEGA = 0.00014584230293413847; // radians/sec
  long size = g->nlev*g->nlat*g->nlon; 
  long gridsize = g->nlat*g->nlon; 
  float *gmh; 
  float *pv;

  // Earth data
  //float RG = 9.80665;
  float Re;
  
  CALLOCF(pv,size);
  CALLOCF(gmh,size);
  
  for (k = nlev-1; k > -1; k--) { // Integrate from the ground up. Loop over levels
    long lev = k*gridsize;
    li = 0; // iterator for lat
    for(i = 0; i < gridsize; i++) {      
      if (i > (li+1)*g->nlon - 1) li++;
      float lat = g->lat[li]*D2R;
      // Calculate the gravity as a function of lat and height (reduced gp)
      // h = gp/G0; GMH = h*Re/(Re*gravity/G0 -h)
      Re = GeoidRadius(lat);
      float hr = gp[lev+i]/G0; // reduced GP to geopotential meter
      gravity = GRAV(lat,hr);
      if (gravity > 10) {
	printf("Grav: %g lat: %f\n",gravity,lat);
	NRERROR("Graivity too high");
      }
      gmh[lev+i] = hr*Re/(gravity*Re/G0 - hr);
      if(i == 0) {
	lming = gravity; 
	lmaxg = gravity;
	lvlgm_max = gmh[lev+i];
	lvlgm_min = gmh[lev+i];
      } else {
	if(gmh[lev+i] > lvlgm_max) lvlgm_max = gmh[lev+i];
	if(gmh[lev+i] < lvlgm_min) lvlgm_min = gmh[lev+i];
	if(gravity < lming) lming = gravity; 
	if(gravity > lmaxg) lmaxg = gravity; 
      }
    }
    if(k == nlev-1) {
      ming = lming;
      maxg = lmaxg;
      gm_max = lvlgm_max;
      gm_min = lvlgm_min;
    } else { 
      if(lvlgm_max > gm_max) gm_max = lvlgm_max;
      if(lvlgm_min < gm_min) gm_min = lvlgm_min;
      if(lming < ming) ming = lming; 
      if(lmaxg > maxg) maxg = lmaxg; 
    }
    if(DEBUG) {
      printf("Level = %03d MaxGMH = %8.3f MinGMH = %8.3f MinG = %f MaxG = %f\n",k,lvlgm_max,lvlgm_min,ming,maxg);
    }
  }
  //EARTH VORTICITY = 2 x (Rate of Rotation of Earth) x sin (Latitude in radians)
  //AV = F + RV Adding the Earths rotational vorticity
  //In this case vorticity is first given as RV in the GRIB file and then converted to PV.
  //The Potential Vorticity is calculated using the formaule (-1/(g))*(ABS VORT)*(dtheta/dp)
  for (k = nlev-1; k > -1; k--) { // The end points will not be calculated
    long uplev = (k-1)*gridsize;
    long lev = k*gridsize;
    long lwrlev = (k+1)*gridsize;
    li = 0; // iterator for lat
    if(k == nlev-1 || k == 0) {
      for(i = 0; i < gridsize; i++) pv[lev+i] = MISSING; // Put at the end points
    } else {
      for(i = 0; i < gridsize; i++) {
	if (i > (li+1)*g->nlon - 1) li++;
	float lat = g->lat[li]*D2R;
	// Calculate the dtheta 
	double dtheta = abs(PT[uplev+i] - PT[lwrlev+i]);
	// Calculate dp
	double dp = abs(P[lwrlev+i] - P[uplev+i]);
	pv[lev+i] = (VO[lev+i] + OMEGA*sin(lat)) * (dtheta/dp)*gravity;
	if(i == 0) {
	  lvlpv_max = pv[lev+i];
	  lvlpv_min = pv[lev+i];
	} else {
	  if(pv[lev+i] > lvlpv_max) lvlpv_max = pv[lev+i];
	  if(pv[lev+i] < lvlpv_min) lvlpv_min = pv[lev+i];
	}
      }// end for loop I
      if(k == nlev-1) {
	pv_max = lvlpv_max;
	pv_min = lvlpv_min;
      } else { 
	if(lvlpv_max > pv_max) pv_max = lvlpv_max;
	if(lvlpv_min < pv_min) pv_min = lvlpv_min;
      }
      if(DEBUG) {
	printf("Level = %03d MaxPV = %10.7f MinPV = %10.7f\n",k,lvlpv_max,lvlpv_min);
      }
    }
  }// end for loop level
  printf("Completed loop over all levels. Calculating the scaling factors and add_offsets\n");

  data *PV = Pack(pv,size,0);
  free(pv); pv = NULL;
  AddAtt(PV,g->PVid,g->d3grp,"PV",g);
  WRITEMD(PV->farray,"f",g->PVid,g->d3grp);
  free(PV->farray); PV = NULL; 

  data *GMH = Pack(gmh,size,1);
  free(gmh); gmh = NULL;
  AddAtt(GMH,g->GMHid,g->d3grp,"GMH",g);
  WRITEMD(GMH->sarray,"s",g->GMHid,g->d3grp);
  free(GMH->sarray); free(GMH); GMH = NULL;
 
  printf("Completed calculation geometric height and potential vorticity\n");

  return;
}

static float GeoidRadius(float lat) {
 
  // [Re] = geoid radius as a  function of latitude calculates the radius of the geoid (m) at the
  //   given latitude radians. If lat is given in radians then lat[i]*DEG2RAD is just lat[i]
  
  float Rmax = EQRAD;
  float Rmin = Rmax*(1.0-FLAT);
  
  return sqrt(1/(pow(cos(lat)/Rmax,2) + pow(sin(lat)/Rmin,2)));
}

void MaxMin(float *array, long size) {
  
  int i;
  float min = array[0];
  float max = array[0];
  
  for(i = 0; i < size; i++) {
    if(array[i] < min) min = array[i];
    if(array[i] > max) max = array[i];
  }
  printf("INFO: Min = %-10f\tMax = %-10f\n",min,max);
  return;
}

void MaxMinS(short *array, long size) {
  
  int i;
  int min = array[0];
  int max = array[0];
  
  for(i = 0; i < size; i++) {
    if(array[i] < min) min = array[i];
    if(array[i] > max) max = array[i];
  }
  printf("INFO: Min = %d\tMax = %d\n",min,max);
  return;
}

static float GRAV(float lat, float z) {

  if(abs(lat)*180/M_PI > 89.5) {
    printf("WARNING Lat > 90 = %f. Setting it to 89.9*M_PI/180\n",lat);
    lat = 89.9*M_PI/180;
  }
  if(z < -1e3  || z > 1000e3) NRERROR("Only altitudes inside [-1,1000] km are allowed.");
  
  // Expression found on web page of UK's National Physical Laboratory
  return 9.780327*( 1 + 0.0053024*pow(sin(lat),2) - 0.0000058*pow(sin(2*lat),2)) - z*3.086*1e-6;
}

static void check_err(const int stat, const int line, const char *file) {
  if (stat != NC_NOERR) {
    (void)fprintf(stderr,"line %d of %s: %s\n", line, file, nc_strerror(stat));
    fflush(stderr);
    exit(1);
  }
}

static void SetupNC(GL *g) {// create cdl.nc 

  int  stat;  // return status 
  int  ncid;  // netCDF id 

  // group ids 
  int root_grp;
  int Geolocation_grp;
  int Data_3D_grp;
  int Data_2D_grp;

  // dimension ids 
  int Geolocation_lon_dim;
  int Geolocation_lat_dim;
  int Geolocation_level_dim;
  int Data_3D_lon_dim;
  int Data_3D_lat_dim;
  int Data_3D_level_dim;
  int Data_2D_lon_dim;
  int Data_2D_lat_dim;

  // dimension lengths 
  size_t Geolocation_lon_len = g->nlon;
  size_t Geolocation_lat_len = g->nlat;
  size_t Geolocation_level_len = g->nlev;
  size_t Data_3D_lon_len = g->nlon;
  size_t Data_3D_lat_len = g->nlat;
  size_t Data_3D_level_len = g->nlev;
  size_t Data_2D_lon_len = g->nlon;
  size_t Data_2D_lat_len = g->nlat;

 
    // variable ids 
    int Geolocation_level_id;
    int Geolocation_lon_id;
    int Geolocation_lat_id;
    int Data_3D_T_id;
    int Data_3D_Q_id;
    int Data_3D_GMH_id;
    int Data_3D_P_id;
    int Data_3D_PV_id;
    int Data_3D_PT_id;
    int Data_3D_GP_id;
    int Data_3D_O3_id;
    int Data_3D_CIWC_id;
    int Data_3D_CLWC_id;
    int Data_3D_U_id;
    int Data_3D_V_id;
    int Data_2D_SP_id;
    int Data_2D_T2M_id;
    int Data_2D_TCW_id;
    int Data_2D_TCWV_id;
    int Data_2D_TCO3_id;
    int Data_2D_MSL_id;
    int Data_2D_Z_id;
    int Data_2D_U10M_id;
    int Data_2D_V10M_id;
    int Data_2D_SKT_id;

    // rank (number of dimensions) for each variable 
#   define RANK_Geolocation_level 1
#   define RANK_Geolocation_lon 1
#   define RANK_Geolocation_lat 1
#   define RANK_Data_3D_T 3
#   define RANK_Data_3D_Q 3
#   define RANK_Data_3D_GMH 3
#   define RANK_Data_3D_P 3
#   define RANK_Data_3D_PV 3
#   define RANK_Data_3D_PT 3
#   define RANK_Data_3D_GP 3
#   define RANK_Data_3D_O3 3
#   define RANK_Data_3D_CIWC 3
#   define RANK_Data_3D_CLWC 3
#   define RANK_Data_3D_U 3
#   define RANK_Data_3D_V 3
#   define RANK_Data_2D_SP 2
#   define RANK_Data_2D_T2M 2
#   define RANK_Data_2D_TCW 2
#   define RANK_Data_2D_TCWV 2
#   define RANK_Data_2D_TCO3 2
#   define RANK_Data_2D_MSL 2
#   define RANK_Data_2D_Z 2
#   define RANK_Data_2D_U10M 2
#   define RANK_Data_2D_V10M 2
#   define RANK_Data_2D_SKT 2

    // variable shapes 
    int Geolocation_level_dims[RANK_Geolocation_level];
    int Geolocation_lon_dims[RANK_Geolocation_lon];
    int Geolocation_lat_dims[RANK_Geolocation_lat];
    int Data_3D_T_dims[RANK_Data_3D_T];
    int Data_3D_Q_dims[RANK_Data_3D_Q];
    int Data_3D_GMH_dims[RANK_Data_3D_GMH];
    int Data_3D_P_dims[RANK_Data_3D_P];
    int Data_3D_PV_dims[RANK_Data_3D_PV];
    int Data_3D_PT_dims[RANK_Data_3D_PT];
    int Data_3D_GP_dims[RANK_Data_3D_GP];
    int Data_3D_O3_dims[RANK_Data_3D_O3];
    int Data_3D_CIWC_dims[RANK_Data_3D_CIWC];
    int Data_3D_CLWC_dims[RANK_Data_3D_CLWC];
    int Data_3D_U_dims[RANK_Data_3D_U];
    int Data_3D_V_dims[RANK_Data_3D_V];
    int Data_2D_SP_dims[RANK_Data_2D_SP];
    int Data_2D_T2M_dims[RANK_Data_2D_T2M];
    int Data_2D_TCW_dims[RANK_Data_2D_TCW];
    int Data_2D_TCWV_dims[RANK_Data_2D_TCWV];
    int Data_2D_TCO3_dims[RANK_Data_2D_TCO3];
    int Data_2D_MSL_dims[RANK_Data_2D_MSL];
    int Data_2D_Z_dims[RANK_Data_2D_Z];
    int Data_2D_U10M_dims[RANK_Data_2D_U10M];
    int Data_2D_V10M_dims[RANK_Data_2D_V10M];
    int Data_2D_SKT_dims[RANK_Data_2D_SKT];

    // enter define mode 
    stat = nc_create(g->outfile, NC_CLOBBER|NC_NETCDF4, &ncid);
    check_err(stat,__LINE__,__FILE__);
    root_grp = ncid;
    stat = nc_def_grp(root_grp, "Geolocation", &Geolocation_grp);
    check_err(stat,__LINE__,__FILE__);
    stat = nc_def_grp(root_grp, "Data_3D", &Data_3D_grp);
    check_err(stat,__LINE__,__FILE__);
    stat = nc_def_grp(root_grp, "Data_2D", &Data_2D_grp);
    check_err(stat,__LINE__,__FILE__);

    // define dimensions 
    stat = nc_def_dim(Geolocation_grp, "lon", Geolocation_lon_len, &Geolocation_lon_dim);
    check_err(stat,__LINE__,__FILE__);
    stat = nc_def_dim(Geolocation_grp, "lat", Geolocation_lat_len, &Geolocation_lat_dim);
    check_err(stat,__LINE__,__FILE__);
    stat = nc_def_dim(Geolocation_grp, "level", Geolocation_level_len, &Geolocation_level_dim);
    check_err(stat,__LINE__,__FILE__);
    stat = nc_def_dim(Data_3D_grp, "lon", Data_3D_lon_len, &Data_3D_lon_dim);
    check_err(stat,__LINE__,__FILE__);
    stat = nc_def_dim(Data_3D_grp, "lat", Data_3D_lat_len, &Data_3D_lat_dim);
    check_err(stat,__LINE__,__FILE__);
    stat = nc_def_dim(Data_3D_grp, "level", Data_3D_level_len, &Data_3D_level_dim);
    check_err(stat,__LINE__,__FILE__);
    stat = nc_def_dim(Data_2D_grp, "lon", Data_2D_lon_len, &Data_2D_lon_dim);
    check_err(stat,__LINE__,__FILE__);
    stat = nc_def_dim(Data_2D_grp, "lat", Data_2D_lat_len, &Data_2D_lat_dim);
    check_err(stat,__LINE__,__FILE__);

    // define variables 

    Geolocation_level_dims[0] = Geolocation_level_dim;
    stat = nc_def_var(Geolocation_grp, "level", NC_INT, RANK_Geolocation_level, Geolocation_level_dims, &Geolocation_level_id);
    check_err(stat,__LINE__,__FILE__);

    Geolocation_lon_dims[0] = Geolocation_lon_dim;
    stat = nc_def_var(Geolocation_grp, "lon", NC_FLOAT, RANK_Geolocation_lon, Geolocation_lon_dims, &Geolocation_lon_id);
    check_err(stat,__LINE__,__FILE__);

    Geolocation_lat_dims[0] = Geolocation_lat_dim;
    stat = nc_def_var(Geolocation_grp, "lat", NC_FLOAT, RANK_Geolocation_lat, Geolocation_lat_dims, &Geolocation_lat_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_T_dims[0] = Data_3D_level_dim;
    Data_3D_T_dims[1] = Data_3D_lat_dim;
    Data_3D_T_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "T", NC_SHORT, RANK_Data_3D_T, Data_3D_T_dims, &Data_3D_T_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_Q_dims[0] = Data_3D_level_dim;
    Data_3D_Q_dims[1] = Data_3D_lat_dim;
    Data_3D_Q_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "Q", NC_FLOAT, RANK_Data_3D_Q, Data_3D_Q_dims, &Data_3D_Q_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_GMH_dims[0] = Data_3D_level_dim;
    Data_3D_GMH_dims[1] = Data_3D_lat_dim;
    Data_3D_GMH_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "GMH", NC_SHORT, RANK_Data_3D_GMH, Data_3D_GMH_dims, &Data_3D_GMH_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_P_dims[0] = Data_3D_level_dim;
    Data_3D_P_dims[1] = Data_3D_lat_dim;
    Data_3D_P_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "P", NC_SHORT, RANK_Data_3D_P, Data_3D_P_dims, &Data_3D_P_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_PV_dims[0] = Data_3D_level_dim;
    Data_3D_PV_dims[1] = Data_3D_lat_dim;
    Data_3D_PV_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "PV", NC_FLOAT, RANK_Data_3D_PV, Data_3D_PV_dims, &Data_3D_PV_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_PT_dims[0] = Data_3D_level_dim;
    Data_3D_PT_dims[1] = Data_3D_lat_dim;
    Data_3D_PT_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "PT", NC_SHORT, RANK_Data_3D_PT, Data_3D_PT_dims, &Data_3D_PT_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_GP_dims[0] = Data_3D_level_dim;
    Data_3D_GP_dims[1] = Data_3D_lat_dim;
    Data_3D_GP_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "GP", NC_SHORT, RANK_Data_3D_GP, Data_3D_GP_dims, &Data_3D_GP_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_O3_dims[0] = Data_3D_level_dim;
    Data_3D_O3_dims[1] = Data_3D_lat_dim;
    Data_3D_O3_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "O3", NC_FLOAT, RANK_Data_3D_O3, Data_3D_O3_dims, &Data_3D_O3_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_CIWC_dims[0] = Data_3D_level_dim;
    Data_3D_CIWC_dims[1] = Data_3D_lat_dim;
    Data_3D_CIWC_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "CIWC", NC_FLOAT, RANK_Data_3D_CIWC, Data_3D_CIWC_dims, &Data_3D_CIWC_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_CLWC_dims[0] = Data_3D_level_dim;
    Data_3D_CLWC_dims[1] = Data_3D_lat_dim;
    Data_3D_CLWC_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "CLWC", NC_FLOAT, RANK_Data_3D_CLWC, Data_3D_CLWC_dims, &Data_3D_CLWC_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_U_dims[0] = Data_3D_level_dim;
    Data_3D_U_dims[1] = Data_3D_lat_dim;
    Data_3D_U_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "U", NC_SHORT, RANK_Data_3D_U, Data_3D_U_dims, &Data_3D_U_id);
    check_err(stat,__LINE__,__FILE__);

    Data_3D_V_dims[0] = Data_3D_level_dim;
    Data_3D_V_dims[1] = Data_3D_lat_dim;
    Data_3D_V_dims[2] = Data_3D_lon_dim;
    stat = nc_def_var(Data_3D_grp, "V", NC_SHORT, RANK_Data_3D_V, Data_3D_V_dims, &Data_3D_V_id);
    check_err(stat,__LINE__,__FILE__);

    Data_2D_SP_dims[0] = Data_2D_lat_dim;
    Data_2D_SP_dims[1] = Data_2D_lon_dim;
    stat = nc_def_var(Data_2D_grp, "SP", NC_SHORT, RANK_Data_2D_SP, Data_2D_SP_dims, &Data_2D_SP_id);
    check_err(stat,__LINE__,__FILE__);

    Data_2D_T2M_dims[0] = Data_2D_lat_dim;
    Data_2D_T2M_dims[1] = Data_2D_lon_dim;
    stat = nc_def_var(Data_2D_grp, "T2M", NC_SHORT, RANK_Data_2D_T2M, Data_2D_T2M_dims, &Data_2D_T2M_id);
    check_err(stat,__LINE__,__FILE__);

    Data_2D_TCW_dims[0] = Data_2D_lat_dim;
    Data_2D_TCW_dims[1] = Data_2D_lon_dim;
    stat = nc_def_var(Data_2D_grp, "TCW", NC_SHORT, RANK_Data_2D_TCW, Data_2D_TCW_dims, &Data_2D_TCW_id);
    check_err(stat,__LINE__,__FILE__);

    Data_2D_TCWV_dims[0] = Data_2D_lat_dim;
    Data_2D_TCWV_dims[1] = Data_2D_lon_dim;
    stat = nc_def_var(Data_2D_grp, "TCWV", NC_SHORT, RANK_Data_2D_TCWV, Data_2D_TCWV_dims, &Data_2D_TCWV_id);
    check_err(stat,__LINE__,__FILE__);

    Data_2D_TCO3_dims[0] = Data_2D_lat_dim;
    Data_2D_TCO3_dims[1] = Data_2D_lon_dim;
    stat = nc_def_var(Data_2D_grp, "TCO3", NC_SHORT, RANK_Data_2D_TCO3, Data_2D_TCO3_dims, &Data_2D_TCO3_id);
    check_err(stat,__LINE__,__FILE__);

    Data_2D_MSL_dims[0] = Data_2D_lat_dim;
    Data_2D_MSL_dims[1] = Data_2D_lon_dim;
    stat = nc_def_var(Data_2D_grp, "MSL", NC_SHORT, RANK_Data_2D_MSL, Data_2D_MSL_dims, &Data_2D_MSL_id);
    check_err(stat,__LINE__,__FILE__);

    Data_2D_Z_dims[0] = Data_2D_lat_dim;
    Data_2D_Z_dims[1] = Data_2D_lon_dim;
    stat = nc_def_var(Data_2D_grp, "Z", NC_SHORT, RANK_Data_2D_Z, Data_2D_Z_dims, &Data_2D_Z_id);
    check_err(stat,__LINE__,__FILE__);

    Data_2D_U10M_dims[0] = Data_2D_lat_dim;
    Data_2D_U10M_dims[1] = Data_2D_lon_dim;
    stat = nc_def_var(Data_2D_grp, "U10M", NC_SHORT, RANK_Data_2D_U10M, Data_2D_U10M_dims, &Data_2D_U10M_id);
    check_err(stat,__LINE__,__FILE__);

    Data_2D_V10M_dims[0] = Data_2D_lat_dim;
    Data_2D_V10M_dims[1] = Data_2D_lon_dim;
    stat = nc_def_var(Data_2D_grp, "V10M", NC_SHORT, RANK_Data_2D_V10M, Data_2D_V10M_dims, &Data_2D_V10M_id);
    check_err(stat,__LINE__,__FILE__);

    Data_2D_SKT_dims[0] = Data_2D_lat_dim;
    Data_2D_SKT_dims[1] = Data_2D_lon_dim;
    stat = nc_def_var(Data_2D_grp, "SKT", NC_SHORT, RANK_Data_2D_SKT, Data_2D_SKT_dims, &Data_2D_SKT_id);
    check_err(stat,__LINE__,__FILE__);

    // assign global attributes 
    { // University 
    stat = nc_put_att_text(root_grp, NC_GLOBAL, "University", 33, "Chalmers University of Technology");
    check_err(stat,__LINE__,__FILE__);
    }
    { // Institude 
    stat = nc_put_att_text(root_grp, NC_GLOBAL, "Institude", 36, "Earth and Space Sciences Institution");
    check_err(stat,__LINE__,__FILE__);
    }
    { // Title 
    stat = nc_put_att_text(root_grp, NC_GLOBAL, "Title", 54, "Basic data for Odin processing and other research uses");
    check_err(stat,__LINE__,__FILE__);
    }
    { // Source 
    stat = nc_put_att_text(root_grp, NC_GLOBAL, "Source", 14, "ECMWF Analysis");
    check_err(stat,__LINE__,__FILE__);
    }
    { // History 
    stat = nc_put_att_text(root_grp, NC_GLOBAL, "History", 44, "Created for GEM group by M. S. Johnston 2011");
    check_err(stat,__LINE__,__FILE__);
    }
    { // Convention 
    stat = nc_put_att_text(root_grp, NC_GLOBAL, "Convention", 40, "Data is stored in 64 bit NETCDF-4 format");
    check_err(stat,__LINE__,__FILE__);
    }
    { // Missing 
    stat = nc_put_att_text(root_grp, NC_GLOBAL, "Missing", 38, "Error or missing data is shown as -999");
    check_err(stat,__LINE__,__FILE__);
    }
    { // Packing 
    stat = nc_put_att_text(root_grp, NC_GLOBAL, "Packing", 38, "Data is stored with a scale and offset");
    check_err(stat,__LINE__,__FILE__);
    }
    { // Resolution 
    stat = nc_put_att_text(root_grp, NC_GLOBAL, "Resolution", 37, "Data is stored on a 1 x 1 degree grid");
    check_err(stat,__LINE__,__FILE__);
    }


    // assign per-variable attributes 
    { // longname 
    stat = nc_put_att_text(Geolocation_grp, Geolocation_level_id, "longname", 6, "Levels");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const int Geolocation_level_FillValue_att[1] = {-999} ;
    stat = nc_put_att_int(Geolocation_grp, Geolocation_level_id, "_FillValue", NC_INT, 1, Geolocation_level_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Geolocation_grp, Geolocation_lon_id, "longname", 9, "longitude");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const float Geolocation_lon_FillValue_att[1] = {-999} ;
    stat = nc_put_att_float(Geolocation_grp, Geolocation_lon_id, "_FillValue", NC_FLOAT, 1, Geolocation_lon_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Geolocation_grp, Geolocation_lon_id, "units", 12, "degrees_east");
    check_err(stat,__LINE__,__FILE__);
    }
    { // axis 
    stat = nc_put_att_text(Geolocation_grp, Geolocation_lon_id, "axis", 1, "X");
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Geolocation_grp, Geolocation_lat_id, "longname", 8, "latitude");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const float Geolocation_lat_FillValue_att[1] = {-999} ;
    stat = nc_put_att_float(Geolocation_grp, Geolocation_lat_id, "_FillValue", NC_FLOAT, 1, Geolocation_lat_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Geolocation_grp, Geolocation_lat_id, "units", 13, "degrees_north");
    check_err(stat,__LINE__,__FILE__);
    }
    { // axis 
    stat = nc_put_att_text(Geolocation_grp, Geolocation_lat_id, "axis", 1, "Y");
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_T_id, "longname", 11, "Temperature");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_3D_T_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_3D_grp, Data_3D_T_id, "_FillValue", NC_SHORT, 1, Data_3D_T_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_T_id, "units", 1, "K");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_T_code_att[1] = {130} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_T_id, "code", NC_INT, 1, Data_3D_T_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_Q_id, "longname", 17, "Specific Humidity");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const float Data_3D_Q_FillValue_att[1] = {-999} ;
    stat = nc_put_att_float(Data_3D_grp, Data_3D_Q_id, "_FillValue", NC_FLOAT, 1, Data_3D_Q_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_Q_id, "units", 9, "kg kg**-1");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_Q_code_att[1] = {133} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_Q_id, "code", NC_INT, 1, Data_3D_Q_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_GMH_id, "longname", 16, "Geometric Height");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_3D_GMH_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_3D_grp, Data_3D_GMH_id, "_FillValue", NC_SHORT, 1, Data_3D_GMH_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_GMH_id, "units", 1, "m");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_GMH_code_att[1] = {-999} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_GMH_id, "code", NC_INT, 1, Data_3D_GMH_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // formula1 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_GMH_id, "formula1", 38, "gmh = hr*Re/(g*Re/G0 - hr), hr = GP/GO");
    check_err(stat,__LINE__,__FILE__);
    }
    { // formula2 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_GMH_id, "formula2", 60, "Re = sqrt(1/(pow(cos(lat)/Remax,2) + pow(sin(lat)/Remin,2)))");
    check_err(stat,__LINE__,__FILE__);
    }
    { // formula3 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_GMH_id, "formula3", 97, "g(lat,z) = 9.780327*( 1 + 0.0053024*pow(sin(lat),2) - 0.0000058*pow(sin(2*lat),2)) - z*3.086*1e-6");
    check_err(stat,__LINE__,__FILE__);
    }
    { // G0 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_GMH_id, "G0", 15, "9.80665 m s**-2");
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_P_id, "longname", 8, "Pressure");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_3D_P_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_3D_grp, Data_3D_P_id, "_FillValue", NC_SHORT, 1, Data_3D_P_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_P_id, "units", 2, "Pa");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_P_code_att[1] = {54} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_P_id, "code", NC_INT, 1, Data_3D_P_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_PV_id, "longname", 19, "Potential Vorticity");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const float Data_3D_PV_FillValue_att[1] = {-999} ;
    stat = nc_put_att_float(Data_3D_grp, Data_3D_PV_id, "_FillValue", NC_FLOAT, 1, Data_3D_PV_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_PV_id, "units", 19, "K m**2 kg**-1 s**-1");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_PV_code_att[1] = {60} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_PV_id, "code", NC_INT, 1, Data_3D_PV_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_PT_id, "longname", 21, "Potential Temperature");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_3D_PT_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_3D_grp, Data_3D_PT_id, "_FillValue", NC_SHORT, 1, Data_3D_PT_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_PT_id, "units", 1, "K");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_PT_code_att[1] = {3} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_PT_id, "code", NC_INT, 1, Data_3D_PT_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_GP_id, "longname", 12, "Geopotential");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_3D_GP_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_3D_grp, Data_3D_GP_id, "_FillValue", NC_SHORT, 1, Data_3D_GP_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_GP_id, "units", 10, "m**2 s**-2");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_GP_code_att[1] = {156} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_GP_id, "code", NC_INT, 1, Data_3D_GP_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_O3_id, "longname", 23, "Ozone mass mixing ratio");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const float Data_3D_O3_FillValue_att[1] = {-999} ;
    stat = nc_put_att_float(Data_3D_grp, Data_3D_O3_id, "_FillValue", NC_FLOAT, 1, Data_3D_O3_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_O3_id, "units", 9, "kg kg**-1");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_O3_code_att[1] = {203} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_O3_id, "code", NC_INT, 1, Data_3D_O3_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_CIWC_id, "longname", 23, "Cloud Ice Water Content");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const float Data_3D_CIWC_FillValue_att[1] = {-999} ;
    stat = nc_put_att_float(Data_3D_grp, Data_3D_CIWC_id, "_FillValue", NC_FLOAT, 1, Data_3D_CIWC_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_CIWC_id, "units", 9, "kg kg**-1");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_CIWC_code_att[1] = {247} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_CIWC_id, "code", NC_INT, 1, Data_3D_CIWC_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_CLWC_id, "longname", 26, "Cloud Liquid Water Content");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const float Data_3D_CLWC_FillValue_att[1] = {-999} ;
    stat = nc_put_att_float(Data_3D_grp, Data_3D_CLWC_id, "_FillValue", NC_FLOAT, 1, Data_3D_CLWC_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_CLWC_id, "units", 9, "kg kg**-1");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_CLWC_code_att[1] = {248} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_CLWC_id, "code", NC_INT, 1, Data_3D_CLWC_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_U_id, "longname", 16, "U wind component");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_3D_U_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_3D_grp, Data_3D_U_id, "_FillValue", NC_SHORT, 1, Data_3D_U_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_U_id, "units", 7, "m s**-1");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_U_code_att[1] = {131} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_U_id, "code", NC_INT, 1, Data_3D_U_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_V_id, "longname", 16, "V wind component");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_3D_V_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_3D_grp, Data_3D_V_id, "_FillValue", NC_SHORT, 1, Data_3D_V_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_3D_grp, Data_3D_V_id, "units", 7, "m s**-1");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_3D_V_code_att[1] = {132} ;
    stat = nc_put_att_int(Data_3D_grp, Data_3D_V_id, "code", NC_INT, 1, Data_3D_V_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_SP_id, "longname", 16, "Surface Pressure");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_2D_SP_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_2D_grp, Data_2D_SP_id, "_FillValue", NC_SHORT, 1, Data_2D_SP_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_SP_id, "units", 2, "Pa");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_2D_SP_code_att[1] = {134} ;
    stat = nc_put_att_int(Data_2D_grp, Data_2D_SP_id, "code", NC_INT, 1, Data_2D_SP_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_T2M_id, "longname", 15, "2 m Temperature");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_2D_T2M_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_2D_grp, Data_2D_T2M_id, "_FillValue", NC_SHORT, 1, Data_2D_T2M_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_T2M_id, "units", 1, "K");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_2D_T2M_code_att[1] = {167} ;
    stat = nc_put_att_int(Data_2D_grp, Data_2D_T2M_id, "code", NC_INT, 1, Data_2D_T2M_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_TCW_id, "longname", 18, "Total Column Water");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_2D_TCW_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_2D_grp, Data_2D_TCW_id, "_FillValue", NC_SHORT, 1, Data_2D_TCW_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_TCW_id, "units", 8, "kg m**-2");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_2D_TCW_code_att[1] = {136} ;
    stat = nc_put_att_int(Data_2D_grp, Data_2D_TCW_id, "code", NC_INT, 1, Data_2D_TCW_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_TCWV_id, "longname", 25, "Total Column Water Vapour");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_2D_TCWV_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_2D_grp, Data_2D_TCWV_id, "_FillValue", NC_SHORT, 1, Data_2D_TCWV_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_TCWV_id, "units", 8, "kg m**-2");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_2D_TCWV_code_att[1] = {137} ;
    stat = nc_put_att_int(Data_2D_grp, Data_2D_TCWV_id, "code", NC_INT, 1, Data_2D_TCWV_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_TCO3_id, "longname", 18, "Total Column Ozone");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_2D_TCO3_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_2D_grp, Data_2D_TCO3_id, "_FillValue", NC_SHORT, 1, Data_2D_TCO3_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_TCO3_id, "units", 8, "kg m**-2");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_2D_TCO3_code_att[1] = {206} ;
    stat = nc_put_att_int(Data_2D_grp, Data_2D_TCO3_id, "code", NC_INT, 1, Data_2D_TCO3_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_MSL_id, "longname", 23, "Mean Sea-Level Pressure");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_2D_MSL_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_2D_grp, Data_2D_MSL_id, "_FillValue", NC_SHORT, 1, Data_2D_MSL_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_MSL_id, "units", 8, "kg m**-2");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_2D_MSL_code_att[1] = {151} ;
    stat = nc_put_att_int(Data_2D_grp, Data_2D_MSL_id, "code", NC_INT, 1, Data_2D_MSL_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_Z_id, "longname", 25, "Orographical Geopotential");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_2D_Z_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_2D_grp, Data_2D_Z_id, "_FillValue", NC_SHORT, 1, Data_2D_Z_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_Z_id, "units", 10, "m**2 s**-2");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_2D_Z_code_att[1] = {129} ;
    stat = nc_put_att_int(Data_2D_grp, Data_2D_Z_id, "code", NC_INT, 1, Data_2D_Z_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // GO 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_Z_id, "GO", 15, "9.80665 m s**-2");
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_U10M_id, "longname", 26, "U Wind component 10 meters");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_2D_U10M_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_2D_grp, Data_2D_U10M_id, "_FillValue", NC_SHORT, 1, Data_2D_U10M_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_U10M_id, "units", 7, "m s**-2");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_2D_U10M_code_att[1] = {165} ;
    stat = nc_put_att_int(Data_2D_grp, Data_2D_U10M_id, "code", NC_INT, 1, Data_2D_U10M_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_V10M_id, "longname", 26, "V Wind component 10 meters");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_2D_V10M_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_2D_grp, Data_2D_V10M_id, "_FillValue", NC_SHORT, 1, Data_2D_V10M_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_V10M_id, "units", 7, "m s**-2");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_2D_V10M_code_att[1] = {166} ;
    stat = nc_put_att_int(Data_2D_grp, Data_2D_V10M_id, "code", NC_INT, 1, Data_2D_V10M_code_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // longname 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_SKT_id, "longname", 16, "Skin Temperature");
    check_err(stat,__LINE__,__FILE__);
    }
    { // _FillValue 
    static const short Data_2D_SKT_FillValue_att[1] = {-999} ;
    stat = nc_put_att_short(Data_2D_grp, Data_2D_SKT_id, "_FillValue", NC_SHORT, 1, Data_2D_SKT_FillValue_att);
    check_err(stat,__LINE__,__FILE__);
    }
    { // units 
    stat = nc_put_att_text(Data_2D_grp, Data_2D_SKT_id, "units", 1, "K");
    check_err(stat,__LINE__,__FILE__);
    }
    { // code 
    static const int Data_2D_SKT_code_att[1] = {235} ;
    stat = nc_put_att_int(Data_2D_grp, Data_2D_SKT_id, "code", NC_INT, 1, Data_2D_SKT_code_att);
    check_err(stat,__LINE__,__FILE__);
	}
	
    // leave define mode 
    stat = nc_enddef (root_grp);
    check_err(stat,__LINE__,__FILE__);	

  // assign variable ids to struct 
  g->oncid = root_grp;
  g->glgrp = Geolocation_grp;
  g->d3grp = Data_3D_grp;
  g->d2grp = Data_2D_grp;

  //printf("root: %d 3d: %d 2d: %d\n",root_grp,Data_3D_grp,Data_2D_grp);
  //printf("root: %d 3d: %d 2d: %d\n",g->oncid,g->d3grp,g->d2grp);
 
  g->lvlid = Geolocation_level_id;	
  g->lonid = Geolocation_lon_id;
  g->latid = Geolocation_lat_id;
  g->Tid = Data_3D_T_id;
  g->Qid = Data_3D_Q_id;
  g->GMHid = Data_3D_GMH_id;
  g->Pid = Data_3D_P_id;
  g->PVid = Data_3D_PV_id;
  g->PTid = Data_3D_PT_id;
  g->GPid = Data_3D_GP_id;
  g->O3id = Data_3D_O3_id;
  g->CIWCid = Data_3D_CIWC_id;
  g->CLWCid = Data_3D_CLWC_id;
  g->Uid = Data_3D_U_id;
  g->Vid = Data_3D_V_id;
  g->SPid = Data_2D_SP_id;
  g->T2Mid = Data_2D_T2M_id;
  g->TCWid = Data_2D_TCW_id;
  g->TCWVid = Data_2D_TCWV_id;
  g->TCO3id = Data_2D_TCO3_id;
  g->MSLid = Data_2D_MSL_id;
  g->Zid = Data_2D_Z_id;
  g->U10Mid = Data_2D_U10M_id;
  g->V10Mid = Data_2D_V10M_id;
  g->SKTid = Data_2D_SKT_id;

  return;
}

static void WRITEMD(void *sar, char *type, int varid, int grpid) {
  
  int retval;
    
  if(DEBUG) printf("Attempting to write to netcdf file!\n");
  if(strcmp(type,"s") == 0) {
    short *ar = (short *)sar;
    if((retval = nc_put_var_short(grpid,varid,&ar[0]))) check_err(retval,__LINE__,__FILE__);
    ar = NULL;
  }
  if(strcmp(type,"f") == 0) {
    float *ar = (float *)sar;
    if((retval = nc_put_var_float(grpid,varid,&ar[0]))) check_err(retval,__LINE__,__FILE__);
    ar = NULL;
  }
  if(DEBUG) printf("Done...\n");
  return;
}

static void WRITE1D(void *sar, char *type, int varid, int grpid) {
  
  int retval;
  if(DEBUG) printf("Attempting to write to netcdf file!\n");
  if(strcmp(type,"i") == 0) { 
    int *ar = (int *)sar;
    if((retval = nc_put_var_int(grpid,varid,&ar[0]))) check_err(retval,__LINE__,__FILE__);
    ar = NULL;
  } else if(strcmp(type,"f") == 0) {  
    float *ar = (float *)sar;
    if((retval = nc_put_var_float(grpid,varid,&ar[0]))) check_err(retval,__LINE__,__FILE__);
    ar = NULL;
  } else {
    NRERROR("This was designed to write GL data of float and int types!");
  }
  if(DEBUG) printf("Done...\n");
  return;
}

static void AddAtt(data *Var, int id, int grpid, char *name, GL *g) {
  
  int stat;
  
  const double scale_factor[1]  = {Var->scale_factor};
  const double add_offset[1] = {Var->add_offset};
  if(DEBUG) {
    printf("Write the scale and offset...\n");
    printf("Root_grp = %d GRPID = %d VARID = %d Name = %s\n",g->oncid,grpid,id,name);
  }

  stat = nc_put_att_double(grpid,id,"scale_factor",NC_DOUBLE,1,scale_factor);
  check_err(stat,__LINE__,__FILE__);
  stat = nc_put_att_double(grpid,id,"add_offset",NC_DOUBLE,1,add_offset);
  check_err(stat,__LINE__,__FILE__);

  if(DEBUG) printf("Added scale and offset :o)\n");
  
  return;
} 

void handle_error(int status, int line, char *file) {
  if (status != NC_NOERR) {
    fprintf(stderr, "%s at line %d in file %s\n", nc_strerror(status),line,file);
    exit(EXIT_FAILURE);
  }
}

// Change the case of strings to lower case
static char *tolowercase(char *vname) {
  int counter=0;
  char mychar;
  char str[100];
  
  while (vname[counter]) {
    mychar=vname[counter];
    str[counter] = tolower(mychar);
    counter++;
  }
  strcpy(vname,str);
  return vname;
}

// Change the case of strings to upper case
static char *touppercase(char *vname) {
  int counter=0;
  char mychar;
  char str[100];
  
  while (vname[counter]) {
    mychar=vname[counter];
    str[counter] = toupper(mychar);
    counter++;
  }
  strcpy(vname,str);
  return vname;
}

