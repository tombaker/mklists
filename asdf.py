
def run_mklists(run_plan: RunPlan) -> None:

    datadirs = [ctx.datadir for ctx in run_plan.datadir_contexts]

    for pass_plan in run_plan.pass_plans:
        if pass_plan.backup_snapshot_dir is not None:

            _init_backup_snapshot_dir(
                backup_snapshot_dir=pass_plan.backup_snapshot_dir,
                repo_configfile=run_ctx.repo_configfile,
                repo_rulefile=run_ctx.repo_rulefile,
            )

            backup_datadirs(
                datadirs=datadirs,
                backup_snapshot_dir=pass_plan.backup_snapshot_dir,
            )

            _prune_backupdirs(
                backup_rootdir=backup_cfg.backup_rootdir,
                backup_depth=backup_cfg.backup_depth,
            )



def backup_datadirs(
    *,
    datadirs: Iterable[Path],
    backup_snapshot_dir: Path,
) -> None:
    """Create backup snapshot for one execution pass.

    Args:
        datadirs: Iterable of datadir paths to snapshot.
        backup_snapshot_dir: Directory for backup snapshot.

    Raises:
        FileExistsError: If backup_snapshot_dir already exists.
    """
    if backup_snapshot_dir.exists():
        raise FileExistsError(
            f"Pass backup directory already exists: {backup_snapshot_dir}"
        )

    backup_snapshot_dir.mkdir(parents=True)
    logger.info(f"Backup {backup_snapshot_dir}")

    for datadir in datadirs:
        target = backup_snapshot_dir / datadir.name
        shutil.copytree(src=datadir, dst=target)

