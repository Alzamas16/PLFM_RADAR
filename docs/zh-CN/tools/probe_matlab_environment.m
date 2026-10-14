% Read-only installed-toolbox and minimal model probes; no project solver.
task_root = fileparts(fileparts(fileparts(fileparts(mfilename('fullpath')))));
record = struct();
record.date = '2026-10-08';
record.version = version;
record.toolboxes = ver;
record.functions = struct();
task_functions = {'physconst','pcbStack','waveguideSlotted','sparameters','rfplot','InitFDTD','InitCSX','RunOpenEMS'};
for k = 1:numel(task_functions)
    record.functions.(task_functions{k}) = which(task_functions{k});
end
record.minimal_models = struct();
try
    task_patch = antenna.Rectangle;
    task_pcb = pcbStack;
    record.minimal_models.antenna_ok = true;
    record.minimal_models.antenna_class = class(task_patch);
    record.minimal_models.pcb_class = class(task_pcb);
catch task_error
    record.minimal_models.antenna_ok = false;
    record.minimal_models.antenna_error = task_error.message;
end
try
    task_sp = sparameters(zeros(2,2,2), [1e9 2e9]);
    record.minimal_models.rf_ok = true;
    record.minimal_models.rf_class = class(task_sp);
catch task_error
    record.minimal_models.rf_ok = false;
    record.minimal_models.rf_error = task_error.message;
end
record.scope = 'Toolbox listing, function resolution, antenna/RF object creation only; no repository simulation or physical measurement.';
task_output = fullfile(task_root,'docs','zh-CN','本机MATLAB环境.json');
task_handle = fopen(task_output,'w','n','UTF-8');
task_cleanup = onCleanup(@() fclose(task_handle));
fprintf(task_handle,'%s\n',jsonencode(record,PrettyPrint=true));
fprintf('ANTENNA_OBJECT_OK=%d\n',record.minimal_models.antenna_ok);
fprintf('RF_OBJECT_OK=%d\n',record.minimal_models.rf_ok);
fprintf('OPENEMS_INIT_PATH=%s\n',record.functions.InitFDTD);
fprintf('REPORT=%s\n',task_output);
