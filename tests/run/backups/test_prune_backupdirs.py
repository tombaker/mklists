"""Tests $MKLRUN/backups.py"""

from mklists.run.backups import prune_backupdirs


def _mk_backupdirs(backup_snapshot_dir, names):
    for name in names:
        (backup_snapshot_dir / name).mkdir()


def test_delete_backupdirs_under_depth(tmp_path):
    """If number of backup directories less than backup depth, delete nothing."""
    names = [
        "2026-02-03_1200",
        "2026-02-03_1300",
        "2026-02-03_1400",
    ]
    _mk_backupdirs(tmp_path, names)

    prune_backupdirs(
        backup_rootdir=tmp_path,
        backup_depth=4,
    )

    assert sorted(p.name for p in tmp_path.iterdir()) == names


def test_delete_backupdirs_exact_depth(tmp_path):
    """If number of backup directories equal to backup depth, delete nothing."""
    names = [
        "2026-02-03_1200",
        "2026-02-03_1300",
        "2026-02-03_1400",
        "2026-02-03_1500",
    ]
    _mk_backupdirs(tmp_path, names)

    prune_backupdirs(
        backup_rootdir=tmp_path,
        backup_depth=4,
    )

    assert sorted(p.name for p in tmp_path.iterdir()) == names


def test_delete_backupdirs_over_depth(tmp_path):
    """If number of backup directories more than backup depth, delete some."""
    names = [
        "2026-02-03_1200",
        "2026-02-03_1300",
        "2026-02-03_1400",
        "2026-02-03_1500",
        "2026-02-03_1600",
        "2026-02-03_1700",
        "2026-02-03_1800",
    ]
    _mk_backupdirs(tmp_path, names)

    prune_backupdirs(
        backup_rootdir=tmp_path,
        backup_depth=4,
    )

    remaining = sorted(p.name for p in tmp_path.iterdir())
    assert remaining == names[-4:]


def test_delete_backupdirs_zero_depth(tmp_path):
    """If backup depth is zero, delete all directories."""
    names = [
        "2026-02-03_1200",
        "2026-02-03_1300",
    ]
    _mk_backupdirs(tmp_path, names)

    prune_backupdirs(
        backup_rootdir=tmp_path,
        backup_depth=0,
    )

    assert not list(tmp_path.iterdir())
