clc;
clear all;
close all;

rng default;

folder = 'sample_data/';
baseFileName = 'global_audio.wav';
fullFileName = fullfile(folder, baseFileName);

%Take input
[mixed_audio,Fs] = audioread(fullFileName);
Fs

n_samples = floor(length(mixed_audio)/Fs)-1;

output = zeros(n_samples,4);

%Calculating inter-split cpsd
k = 1;
for i = 1:Fs:length(mixed_audio)-2*Fs
    x = mixed_audio(i:i+Fs,1);
    y = mixed_audio(i+Fs:i+2*Fs,1);
    output(k,:)= [i i+Fs i+2*Fs sum(abs(cpsd(x,y)))];%Taking the sum of the absolute value of the entire cpsd vector
    k = k+1;
end

%Range of k for k-means
klist=(2:6);

%Find the optimal value of k with Silhoutte index
E = evalclusters(output(:,4),'kmeans','silhouette','klist',klist);

%Plotting the Silhoutte score
figure;
plot(E)

%Cluster with optimal value of k
[IDX, C] = kmeans(output(:,4),E.OptimalK);

%Check the distributions of each cluster
figure;
boxplot(output(:,4),IDX)

% %Decorating the boxplot
% colors = rand(3,3);
% h = findobj(gca,'Tag','Box');
% for j=1:length(h)
%     patch(get(h(j),'XData'),get(h(j),'YData'),colors(j,:),'FaceAlpha',.2,'LineWidth',2);
% end
% h = findobj(gca,'Tag','Median');
% set(h,'linew',2);
% h = findobj(gca,'Tag','Outliers');
% set(h,'linew',2);
% h = findobj('-regexp','Tag','(Lower|Upper) (Whisker|Adjacent Value)');
% set(h,'linew',2);

%Choose the cluster index with minimal value
[val,pos] = min(C);

disp('The cluster with minimum mean');
disp(pos);

%Choose the split positions having lower mean
choose_split_positions = [];
j=1;
startPos = 1;
endPos = 1;
for i = 1:n_samples
    if IDX(i)==pos
        endPos = output(i,2);
        choose_split_positions(j,:)=[startPos endPos];
        startPos = endPos;
        j=j+1;
    end
end
choose_split_positions(j,:)=[startPos output(length(output),3)];

%Delete the content of the cpsd_splits directory
delete([folder,'cpsd_splits/*.wav'])

%Read the synchronized global time
baseFileName = 'global_audio_log.csv';
fullFileName = fullfile(folder, baseFileName);
data = fopen(fullFileName);
A = textscan(data,'%s','Delimiter','\n');
B = split(A{1,1}(2),',');
B = B(1);
dt = datetime(B, 'InputFormat', 'HH:mm:ss.SSSSS');
fclose(data);

%Primary file for split positions and split id
fileID = fopen(fullfile(folder,'split_info.csv'),'wt');
fprintf(fileID,'splitid,start-time,end-time\n');

%Split audio at the chosen positions
for i = 1:length(choose_split_positions)
    audiowrite([folder 'cpsd_splits/split_' num2str(i) '.wav'],mixed_audio(choose_split_positions(i,1):choose_split_positions(i,2)),Fs);
    startTime = dt + seconds(choose_split_positions(i,1)/Fs);
    startTime.Format = 'HH:mm:ss.SSSSS';
    endTime = dt + seconds(choose_split_positions(i,2)/Fs);
    endTime.Format = 'HH:mm:ss.SSSSS';
    fprintf(fileID,'%s,%13s,%13s\n',['split_' num2str(i)],startTime,endTime);
end
fclose(fileID);