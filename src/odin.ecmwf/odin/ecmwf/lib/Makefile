CC = gcc 
LD = gcc 
LDSHARED = $(CC)
HOME = /home/marston/SOFTWARE

INC= -I$(HOME)/libs4cdo-0.0.9/build/include -I$/usr/include 

LIB= -L$(HOME)/libs4cdo-0.0.9/build/lib -L/usr/lib

LIBRARIES= -lnetcdf -lhdf5_hl -lhdf5 -lcurl -lz -lm 

#FLAGS
#CFLAGS= -static -g -O2 -Wall -z $(INC) 
CFLAGS= -g -Wall -O2 -z muldefs $(HDF5INC) $(NCINC) 

#LINKER FLAGS
#LDFLAGS= -static -static-libgcc $(LIB)
LDFLAGS= --as-needed $(HDF5LIB) $(NCLIB) 

#------------------------------------------------------------------
#List of generated object files for adding
OBJECTS= odinecmwf2.o 

#Top-level rule, to compile area
TARGET= ODINP_GRIB2
grib2: $(TARGET) 

#Rule to link the program
$(TARGET): $(OBJECTS)
	$(LDSHARED) -o $(TARGET) $(OBJECTS) $(LDFLAGS) $(LIBRARIES)

#Rule per dependency when compiling
odinecmwf2.o: odinecmwf2.c 
	$(CC) $(CFLAGS) -c odinecmwf2.c
#--------------------------------------------------------------------
#Top-level rule, to compile area
TARGET= ODINP_GRIB1
grib1: $(TARGET) 

#Rule to link the program
$(TARGET): $(OBJECTS)
	$(LDSHARED) -o $(TARGET) $(OBJECTS) $(LDFLAGS) $(LIBRARIES)

#Rule per dependency when compiling
odinecmwf1.o: odinecmwf1.c 
	$(CC) $(CFLAGS) -c odinecmwf1.c
#---------------------------------------------------------
clean:
	@\rm -f *.o *~

