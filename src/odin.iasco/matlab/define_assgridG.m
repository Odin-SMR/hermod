function [II_ass2d,Roo_x,Roo_y,Rob_x,Rob_y]=define_assgridG(xobs,yobs,II_dx,II_dy,N_Lat,N_Long);


%II_ass2d is given the indexes to the 2D latitude-longitude model grid points that are to be
%influenced by assimilation. 
II_ass2d=[];
for i=1:length(xobs)
    
    I=intersect(find((yobs(i)+II_dy)>0),find((yobs(i)+II_dy)<=N_Lat));
    
    II=yobs(i)+(xobs(i)-1)*N_Lat+II_dx(I)*N_Lat+II_dy(I);
    
    
    II(find(II<1))=II(find(II<1))+N_Lat*N_Long;
    II(find(II>N_Lat*N_Long))=II(find(II>N_Lat*N_Long))-N_Lat*N_Long;
   
    II_ass2d=union(II_ass2d,II);
end

yass=mod(II_ass2d,N_Lat);
xass=ceil(II_ass2d/N_Lat);


%Roo_x is given the square of the zonal distances between observation points.
Roo_x=(repmat(xobs,1,length(xobs))-repmat(xobs',length(xobs),1));
%Special care is taken when the observation vector crosses the 180 degree
%longitude
Roo_x(find(Roo_x>N_Long*.7))=N_Long-Roo_x(find(Roo_x>N_Long*.7));
Roo_x=Roo_x.^2;


%Rob_x is given the square of the zonal distances between observation and
%assimilation points
Rob_x=(repmat(xobs,1,length(II_ass2d))-repmat(xass',length(xobs),1));
Rob_x(find(Rob_x>N_Long*.7))=N_Long-Rob_x(find(Rob_x>N_Long*.7));
Rob_x=Rob_x.^2;

%Roo_y and Rob_y are like Roo_x and Rob_x but for meridional distances
Roo_y=(repmat(yobs,1,length(yobs))-repmat(yobs',length(yobs),1)).^2;
Rob_y=(repmat(yobs,1,length(II_ass2d))-repmat(yass',length(yobs),1)).^2;