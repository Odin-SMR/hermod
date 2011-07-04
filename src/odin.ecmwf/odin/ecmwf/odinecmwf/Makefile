CC = gcc 
LD = gcc 
LDSHARED = $(CC)
HOME = /home/marston/SOFTWARE

INC= -I$(HOME)/libs4cdo-0.0.9/build/include -I$/usr/include 

LIB= -L$(HOME)/libs4cdo-0.0.9/build/lib -L/usr/lib

LIBRARIES= -lnetcdf -lhdf5_hl -lhdf5 -lcurl -lz -lm 

#FLAGS
#CFLAGS= -static -g -O2 -Wall -z $(INC) 
CFLAGS= -g -fpic -Wall -O2 -z muldefs $(HDF5INC) $(NCINC) 
 
#LINKER FLAGS
#LDFLAGS= -static -static-libgcc $(LIB)
LDFLAGS= --shared -Wl,-soname,odinp_grib2.so.1 $(HDF5LIB) $(NCLIB) 

#------------------------------------------------------------------
#List of generated object files for adding
OBJECTS2= odinecmwf_grib2.o 

#Top-level rule, to compile area
TARGET2= odinp_grib2.so.1.0.0
grib2: $(TARGET2) 

#Rule to link the program
$(TARGET2): $(OBJECTS2)
	$(LDSHARED) -o $(TARGET2) $(OBJECTS2) $(LDFLAGS) $(LIBRARIES)

#Rule per dependency when compiling
odinecmwf2.o: odinecmwf_grib2.c 
	$(CC) $(CFLAGS) -c odinecmwf_grib2.c
#--------------------------------------------------------------------
#List of generated object files for adding
OBJECTS1= odinecmwf_grib1.o 
#Top-level rule, to compile area
TARGET1= odinp_grib1.so
grib1: $(TARGET1) 

#Rule to link the program
$(TARGET1): $(OBJECTS1)
	$(LDSHARED) -o $(TARGET1) $(OBJECTS1) $(LDFLAGS) $(LIBRARIES)

#Rule per dependency when compiling
odinecmwf1.o: odinecmwf_grib1.c 
	$(CC) $(CFLAGS) -c odinecmwf_grib1.c
#---------------------------------------------------------
clean:
	@\rm -f *.o *~

