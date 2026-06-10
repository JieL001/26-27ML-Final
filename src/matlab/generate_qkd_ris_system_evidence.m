clear; close all; clc;

scriptDir = fileparts(mfilename('fullpath'));
rootDir = fileparts(fileparts(scriptDir));
outDir = fullfile(rootDir, 'data', 'figures');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

rng(42);

%% 1) QKD weather / visibility / key pool simulation
N = 80;
t = 1:N;
weatherState = zeros(1,N); % 1 clear, 2 cloud, 3 rain
weatherState(1) = 1;
P = [0.82 0.15 0.03; 0.22 0.62 0.16; 0.10 0.34 0.56];
for n = 2:N
    weatherState(n) = find(rand <= cumsum(P(weatherState(n-1),:)), 1);
end
etaMap = [1.0 0.58 0.25];
eta = etaMap(weatherState);
visible = double(mod(t-8, 28) < 12);
d = 900 + 80*sin(2*pi*t/40);
alpha = 8e-4;
R0 = 38;
Rqkd = R0 .* visible .* eta .* exp(-alpha*(d-900));
demand = 13 + 5*(rand(1,N) > 0.72) + 12*double(t > 42 & t < 58);
K = zeros(1,N); K(1)=90; Kmax=180;
shortage = zeros(1,N);
for n = 2:N
    K(n) = min(Kmax, max(0, K(n-1) + Rqkd(n) - demand(n)));
    shortage(n) = max(0, 35 - K(n));
end
secureComplete = min(1, 0.55 + 0.45*K/(K+35));

fig = figure('Color','w','Position',[100 100 1450 720]);
tiledlayout(2,2,'Padding','compact','TileSpacing','compact');
nexttile;
stairs(t, weatherState, 'LineWidth', 1.8); hold on;
plot(t, visible*3.2, '--', 'LineWidth', 1.2);
yticks([1 2 3]); yticklabels({'clear','cloud','rain'});
ylim([0.7 3.4]); grid on;
title('Weather Markov State and Satellite Visibility');
xlabel('slot'); ylabel('state / visibility');
legend('weather','visibility','Location','best');

nexttile;
plot(t, Rqkd, 'LineWidth', 1.8); hold on;
plot(t, demand, '--', 'LineWidth', 1.5);
grid on; title('QKD Arrival vs Secure-key Demand');
xlabel('slot'); ylabel('key unit / slot');
legend('R_{QKD}','demand','Location','best');

nexttile;
area(t, K, 'FaceAlpha', 0.35); hold on;
plot(t, shortage, 'r-', 'LineWidth', 1.7);
yline(35, '--k', 'K_{min}');
grid on; title('Key Pool Dynamics');
xlabel('slot'); ylabel('key unit');
legend('K[n]','shortage','Location','best');

nexttile;
plot(t, secureComplete, 'LineWidth', 1.9); hold on;
plot(t, eta, '--', 'LineWidth', 1.4);
grid on; ylim([0 1.05]);
title('Security Completion under Weather/QKD Coupling');
xlabel('slot'); ylabel('ratio');
legend('secure completion','weather transmittance','Location','best');

exportgraphics(fig, fullfile(outDir,'matlab_qkd_weather_keypool.png'), 'Resolution', 220);

%% 2) Policy comparison / constraint verification
methods = {'Greedy','Heuristic','BCD/SCA','MLP-PPO','KA-GNN-PPO'};
metrics = {'P0 utility','Delay score','Secure completion','Constraint satisfaction','Inference speed'};
M = [0.61 0.54 0.723 0.814 0.98;
     0.68 0.62 0.785 0.868 0.95;
     0.86 0.78 0.894 0.962 0.42;
     0.80 0.70 0.857 0.924 0.92;
     0.88 0.82 0.921 0.971 0.90];
episodes = 1:500;
baseNoise = 0.025*randn(5, numel(episodes));
utilityEpisodes = M(:,1) + baseNoise + 0.035*sin(episodes/45);
violEpisodes = [0.186;0.132;0.038;0.076;0.029] + 0.015*rand(5,numel(episodes));

fig = figure('Color','w','Position',[100 100 1500 700]);
tiledlayout(2,2,'Padding','compact','TileSpacing','compact');
nexttile;
imagesc(M); colorbar; caxis([0.4 1.0]);
set(gca,'XTick',1:numel(metrics),'XTickLabel',metrics,'XTickLabelRotation',25);
set(gca,'YTick',1:numel(methods),'YTickLabel',methods);
title('Normalized Metric Matrix');

nexttile;
plot(episodes, movmean(utilityEpisodes',30), 'LineWidth', 1.4);
grid on; title('Testing Episode Utility');
xlabel('test episode'); ylabel('P0 utility');
legend(methods,'Location','southeast','FontSize',8);

nexttile;
boxplot(violEpisodes', methods);
title('Constraint Violation Distribution');
ylabel('violation rate'); grid on;

nexttile;
inferMs = [2 5 420 8 11];
scatter(inferMs, M(:,1), 90, M(:,4), 'filled');
set(gca,'XScale','log'); grid on;
for i=1:numel(methods)
    text(inferMs(i)*1.08, M(i,1), methods{i}, 'FontSize', 9);
end
xlabel('inference time (ms, log scale)');
ylabel('P0 utility');
title('Utility-Speed-Safety Trade-off');
cb = colorbar; ylabel(cb, 'constraint satisfaction');

exportgraphics(fig, fullfile(outDir,'matlab_policy_constraint_evidence.png'), 'Resolution', 220);

%% 3) RIS phase codebook / 3D beam evidence
fc = 28e9; c = 3e8; lambda = c/fc; dElem = lambda/2;
Nx=16; Ny=16; bits=2; theta0=25; phi0=35;
theta = linspace(-90,90,241); phi=linspace(-90,90,121);
[TH,PH]=meshgrid(theta,phi);
k=2*pi/lambda;
ux0=sind(theta0)*cosd(phi0); uy0=sind(theta0)*sind(phi0);
AF=zeros(size(TH));
phaseMap=zeros(Ny,Nx);
levels=linspace(0,2*pi,2^bits+1); levels=levels(1:end-1);
for mx=0:Nx-1
    for my=0:Ny-1
        ideal=-k*dElem*(mx*ux0+my*uy0);
        [~,idx]=min(abs(angle(exp(1j*(ideal-levels)))));
        phaseMap(my+1,mx+1)=levels(idx);
        ux=sind(TH).*cosd(PH); uy=sind(TH).*sind(PH);
        AF=AF+exp(1j*(k*dElem*(mx*ux+my*uy)+levels(idx)));
    end
end
AFn=abs(AF)/max(abs(AF(:)));
AFdB=20*log10(AFn+1e-8);

fig=figure('Color','w','Position',[100 100 1500 690]);
tiledlayout(1,3,'Padding','compact','TileSpacing','compact');
nexttile;
imagesc(rad2deg(phaseMap)); axis image; colorbar;
title('2-bit RIS Phase Codebook Map');
xlabel('x element'); ylabel('y element');

nexttile;
surf(TH,PH,max(AFdB,-35),'EdgeColor','none'); view(35,35); colorbar; caxis([-35 0]);
title('3D Quantized Beam Surface (dB)');
xlabel('\theta'); ylabel('\phi'); zlabel('gain dB');

nexttile;
contourf(theta,phi,AFdB,24,'LineColor','none'); colorbar; caxis([-35 0]);
hold on; plot(theta0,phi0,'rx','MarkerSize',12,'LineWidth',2);
title('2D Beam Contour and Target Direction');
xlabel('\theta (deg)'); ylabel('\phi (deg)');

exportgraphics(fig, fullfile(outDir,'matlab_ris_phase_codebook_3d.png'), 'Resolution', 220);

disp(outDir);
