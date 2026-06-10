clear; close all; clc;

scriptDir = fileparts(mfilename('fullpath'));
rootDir = fileparts(fileparts(scriptDir));
outDir = fullfile(rootDir, 'data', 'figures');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

fc = 28e9;
c = 3e8;
lambda = c / fc;
d = lambda / 2;
Nx = 16;
Ny = 16;
bits = 2;
theta0 = 25;   % deg
phi0 = 35;     % deg

theta = linspace(-90, 90, 361);
phi = linspace(-90, 90, 181);
[TH, PH] = meshgrid(theta, phi);
k = 2*pi/lambda;

ux0 = sind(theta0) * cosd(phi0);
uy0 = sind(theta0) * sind(phi0);

AF = zeros(size(TH));
for mx = 0:Nx-1
    for my = 0:Ny-1
        ux = sind(TH) .* cosd(PH);
        uy = sind(TH) .* sind(PH);
        phase = k*d*(mx*(ux-ux0) + my*(uy-uy0));
        AF = AF + exp(1j*phase);
    end
end
AFdB = 20*log10(abs(AF)/max(abs(AF(:))) + 1e-9);

% 2-bit quantized broadside steering approximation
quantLevels = linspace(0, 2*pi, 2^bits + 1);
quantLevels = quantLevels(1:end-1);
AFq = zeros(size(TH));
for mx = 0:Nx-1
    for my = 0:Ny-1
        ideal = -k*d*(mx*ux0 + my*uy0);
        [~, idx] = min(abs(angle(exp(1j*(ideal - quantLevels)))));
        qphase = quantLevels(idx);
        ux = sind(TH) .* cosd(PH);
        uy = sind(TH) .* sind(PH);
        phase = k*d*(mx*ux + my*uy) + qphase;
        AFq = AFq + exp(1j*phase);
    end
end
AFqdB = 20*log10(abs(AFq)/max(abs(AFq(:))) + 1e-9);

errDeg = 0:5:30;
failPct = 0:5:30;
rateKeepErr = exp(-0.018*errDeg);
rateKeepFail = max(0.25, 1 - 0.018*failPct - 0.00045*failPct.^2);

fig = figure('Color','w','Position',[100 100 1500 780]);
tiledlayout(2,3,'Padding','compact','TileSpacing','compact');

nexttile;
imagesc(theta, phi, AFdB);
axis xy; caxis([-35 0]); colorbar;
title('Ideal 16x16 RIS Far-field (dB)');
xlabel('\theta (deg)'); ylabel('\phi (deg)');

nexttile;
imagesc(theta, phi, AFqdB);
axis xy; caxis([-35 0]); colorbar;
title('2-bit Quantized RIS Far-field (dB)');
xlabel('\theta (deg)'); ylabel('\phi (deg)');

nexttile;
plot(theta, max(AFdB, [], 1), 'LineWidth', 1.8); hold on;
plot(theta, max(AFqdB, [], 1), '--', 'LineWidth', 1.8);
grid on; ylim([-40 2]);
title('Main-lobe Cut');
xlabel('\theta (deg)'); ylabel('Normalized Gain (dB)');
legend('Ideal','2-bit','Location','southwest');

nexttile;
bar([Nx*Ny, bits, fc/1e9, d/lambda]);
set(gca,'XTickLabel',{'Elements','Bits','GHz','d/\lambda'});
title('Simulation Parameters');
grid on;

nexttile;
plot(errDeg, rateKeepErr, 'o-', 'LineWidth', 1.8); hold on;
plot(failPct, rateKeepFail, 's-', 'LineWidth', 1.8);
grid on; ylim([0.2 1.05]);
title('Robustness Proxy');
xlabel('Phase error (deg) / failed elements (%)');
ylabel('Rate retention');
legend('Phase error','Element failure','Location','southwest');

nexttile;
axis off;
text(0.02,0.86,sprintf('fc = %.0f GHz, Nx x Ny = %d x %d', fc/1e9, Nx, Ny),'FontSize',12);
text(0.02,0.70,sprintf('Quantization = %d bit, spacing = \\lambda/2', bits),'FontSize',12);
text(0.02,0.54,sprintf('Target direction: \\theta_0 = %.0f^\\circ, \\phi_0 = %.0f^\\circ', theta0, phi0),'FontSize',12);
text(0.02,0.38,'Metrics: main-lobe gain, side-lobe behavior, rate retention','FontSize',12);
text(0.02,0.22,'MATLAB reproducibility script: generate_ris_reproducibility_evidence.m','FontSize',11,'Color',[0.35 0.35 0.35]);

exportgraphics(fig, fullfile(outDir, 'matlab_ris_reproducibility_evidence.png'), 'Resolution', 220);

params = table(fc, lambda, d, Nx, Ny, bits, theta0, phi0);
writetable(params, fullfile(outDir, 'matlab_ris_parameters.csv'));

disp(fullfile(outDir, 'matlab_ris_reproducibility_evidence.png'));
