function [dR,Err_new,Chi2,N_chi]=assimilateG(R_obs,Err_obs,Err_ass,...
    OZON,OZON_QUALITY,Roo_x,Roo_y,Rob_x,Rob_y,L_ass);

if isempty(OZON)
    dR=[];
    Err_new=[];
    Chi2=[];
    N_chi=[];
else
    
    dR=[];
    Err_new=[];
    Chi2=[];
    N_chi=[];
    for i=1:size(R_obs,2)
        R2oo_x=Roo_x/L_ass;
        R2oo_y=Roo_y/L_ass;
        R2ob_x=Rob_x/L_ass;
        R2ob_y=Rob_y/L_ass;
        
      
        Err_o=Err_obs(:,i);
        Err_a=Err_ass(:,i);
        
        
        S_ap=Err_o*Err_a'.*exp(-.5*(R2ob_x+R2ob_y));
        S_op=diag(OZON_QUALITY(:,i)).^2+Err_o*Err_o'.* ...
            exp(-.5*(R2oo_x+R2oo_y));
        W=S_op\S_ap;
        
        
        dO3=OZON(:,i)-R_obs(:,i);
        dR=[dR W'*dO3];
        
        
        Err_new=[Err_new abs(sqrt(Err_ass(:,i).^2-sum(W.*S_ap,1)'))];
        
        
        II=find(dO3~=0);
        dO3=dO3(II);
        L_chi=length(dO3);
        S_op_inv=inv(S_op(II,II));
        
        N_chi=[N_chi L_chi];
        if L_chi>0
            Chi2=[Chi2 dO3'*S_op_inv*dO3/L_chi];
        else
            Chi2=[Chi2 nan];
        end
    end
end
