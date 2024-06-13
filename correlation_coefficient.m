%% Compute correlation coefficient values between data and model of GPS time series
% Rino Salman, 13 June 2024
% EOS-RS Lab, NTU, Singapore

%% compute correlation coefficient
gpsSites=['CTCN';'CTRA';'CPSU';'CPWJ';'CMUS';'CLSN';'CANA';'CBJY';'CBKA';'CBTH';'CKAG';'CKMN';'CKRI';'CLHT';'CMEN';'CMTP';'CPBM';'CSEK';'KRUI';'MNNA';'PALE';'TJKG'];
corr_coef_all_sites = [];
for i=1:22

    % data
    fidtextdata = ['../output/',gpsSites(i,:),'_clean_Noff1site.rneu'];
    fiddata = fopen(fidtextdata,'rt');
    fidreaddata = textscan(fiddata,'%f%f%f%f%f%f%f%f','HeaderLines',3);
    fclose(fiddata);
    [yearmdoy,yeardcml,N,E,U,Ne,Ee,Ue] = fidreaddata{1:8};
    fprintf('Reading station: %s\n',gpsSites(i,:))

    % model
    fidtextmodel = ['../output/',gpsSites(i,:),'_clean_Noff2model.rneu'];
    fidmodel = fopen(fidtextmodel,'rt');
    fidreadmodel = textscan(fidmodel,'%f%f%f%f%f%f%f%f','HeaderLines',3);
    fclose(fidmodel);
    [yearmdoymod,~,Nmod,Emod,Umod,~,~,~] = fidreadmodel{1:8};
    % grab the same datasets
    NmodFilt = []; EmodFilt = []; UmodFilt = [];
    for j=1:numel(yearmdoy)
        for k=1:numel(yearmdoymod)
            if yearmdoymod(k)==yearmdoy(j)
                Ntemp=Nmod(k);
                Etemp=Emod(k);
                Utemp=Umod(k);
            end
        end
        NmodFilt = [NmodFilt;Ntemp];
        EmodFilt = [EmodFilt;Etemp];
        UmodFilt = [UmodFilt;Utemp];
    end

    % compute the correlation
    corr_coef_N = corr(N(:),NmodFilt(:));
    corr_coef_E = corr(E(:),EmodFilt(:));
    corr_coef_U = corr(U(:),UmodFilt(:));
    temp_corr_coef = [corr_coef_E,corr_coef_N,corr_coef_U];
    corr_coef_all_sites = [corr_coef_all_sites;temp_corr_coef];

end

%% data velocities
fid = fopen('../output/extract_clean.vel','rt');
fidread = textscan(fid,'%s%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f','HeaderLines',4);
fclose(fid);
[Sta,Lon,Lat,Height,VE,VN,VU,ErE,ErN,ErU,Weight,T0,T0D,T1,T1D,Cne] = fidread{1:16};

%% save
temp = [Lon,Lat,VE,VN,VU,corr_coef_all_sites];
temp2 = [Sta,num2cell(temp)];
mytitle = {'#SiteName' 'Lon' 'Lat' 'Ve' 'Vn' 'Vu' 'CorrCoef_E' 'CorrCoef_N' 'CorrCoef_U'};
temp3 = [mytitle;temp2];
writecell(temp3,'GPS_velocities_corr_coeff_Sunda.txt','Delimiter','space')




