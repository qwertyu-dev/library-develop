import os
import pytest
import shutil
from pathlib import Path

class MockSFTPClient:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
    
    def put(self, local_path, remote_path):
        """ファイルをアップロード"""
        dest = self.root_dir / self._normalize_path(remote_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_path, dest)
    
    def get(self, remote_path, local_path):
        """ファイルをダウンロード"""
        src = self.root_dir / self._normalize_path(remote_path)
        shutil.copy2(src, local_path)
    
    def listdir(self, path='.'):
        """ディレクトリの内容を一覧表示"""
        target_dir = self.root_dir / self._normalize_path(path)
        return [f.name for f in target_dir.iterdir()]
    
    def mkdir(self, path):
        """ディレクトリを作成"""
        new_dir = self.root_dir / self._normalize_path(path)
        new_dir.mkdir(parents=True, exist_ok=True)
    
    def remove(self, path):
        """ファイルを削除"""
        target = self.root_dir / self._normalize_path(path)
        if target.is_file():
            target.unlink()
    
    def _normalize_path(self, path):
        """パスを正規化"""
        return Path(path.lstrip('/'))

class MockSFTPConnection:
    def __init__(self, root_dir):
        self.sftp = MockSFTPClient(root_dir)
    
    def __enter__(self):
        return self.sftp
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.fixture
def mock_sftp(tmp_path):
    """SFTPクライアントのモック"""
    sftp_root = tmp_path / 'sftp_root'
    return MockSFTPConnection(sftp_root)

def test_sftp_basic_operations(mock_sftp, tmp_path):
    """基本的なSFTP操作のテスト"""
    with mock_sftp as sftp:
        # テストファイルを作成
        test_file = tmp_path / 'test.txt'
        test_file.write_text('Hello, SFTP World!')
        
        # アップロード
        sftp.put(test_file, '/remote/test.txt')
        
        # ディレクトリ一覧を確認
        assert 'test.txt' in sftp.listdir('/remote')
        
        # ダウンロード
        download_path = tmp_path / 'downloaded.txt'
        sftp.get('/remote/test.txt', download_path)
        
        # 内容を確認
        assert download_path.read_text() == 'Hello, SFTP World!'

def test_sftp_directory_operations(mock_sftp):
    """ディレクトリ操作のテスト"""
    with mock_sftp as sftp:
        # ディレクトリを作成
        sftp.mkdir('/test_dir')
        sftp.mkdir('/test_dir/sub_dir')
        
        # ディレクトリの存在を確認
        assert 'test_dir' in sftp.listdir('/')
        assert 'sub_dir' in sftp.listdir('/test_dir')

def test_sftp_file_operations(mock_sftp, tmp_path):
    """ファイル操作のテスト"""
    with mock_sftp as sftp:
        # テストファイルを作成してアップロード
        test_file = tmp_path / 'test.txt'
        test_file.write_text('Test Content')
        sftp.put(test_file, '/test.txt')
        
        # ファイルの存在を確認
        assert 'test.txt' in sftp.listdir('/')
        
        # ファイルを削除
        sftp.remove('/test.txt')
        assert 'test.txt' not in sftp.listdir('/')
