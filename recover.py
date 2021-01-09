""" toftRecovery Tool (Python 3)

Recover an original file from 3 different corrupted copies (2-of-3 Recovery)

"""

import sys
import hashlib

from os import listdir
from os.path import isfile, join
from time import sleep

# we have the sha256sum of the original file
original_sha256sum = "1f409f67f131db30d5f7ecc9b29e3e4d5c4b0fe9d8600451efdcdef5f4dccef9"
recovery_filepath = "recovered.jpeg"


 
# level of branching tree
branching_level = 8
fork_branch_limit = 3 ** branching_level


corrupted_dir = "./samples/"  #: load corrupted files from this directory


def _get_corrupted_filenames(corrupted_dir):
	"""
	Args:
		corrupted_dir (str): path to corrupted files directory

	Returns:
		corrupted_files (list): list of file names
	"""

	corrupted_files = [f for f in listdir(corrupted_dir) if isfile(join(corrupted_dir, f))]
	if len(corrupted_files) != 3:
		print(f"Exactly 3 files must be in the corrupted_dir but you have: {len(corrupted_files)}")
		sys.exit()
	return corrupted_files


def load_file(filename):
	with open(filename, "rb") as file_byte:
		return file_byte.read()


def load_files_from_dir(corrupted_dir):
	print(f"loading files from directory: {corrupted_dir}")
	corrupted_files = _get_corrupted_filenames(corrupted_dir)
	for file in corrupted_files:
		path = corrupted_dir + file
		file = load_file(path)
		yield file


def write_recover_file(recovered_bytes, filename):
	with open(filename, "wb") as f:
		f.write(recovered_bytes)
		f.close()
	print("write_recover_file: OK")


def recover_bytes_2_of_3(file1, file2, file3):
	forks = []
	recovered_bytes = b""

	forks.append(recovered_bytes)

	# iterate bytes through 3 versions
	for i in range(len(file1)):
		temp_forks = []
		# print(i)
		byte_v1 = file1[i].to_bytes(1, "little")
		byte_v2 = file2[i].to_bytes(1, "little")
		byte_v3 = file3[i].to_bytes(1, "little")
		candidates = [byte_v1, byte_v2, byte_v3]

		# keep byte value if at least two versions are matching
		majority_vote = [b for b in candidates if candidates.count(b) >= 2]

		if not majority_vote:
			# Same byte is corrupted in at least 2 files
			# We can't have high level of confidence
			# Therefore keeping all the values 
			# and forking reconstruction bytes into 3 new branches
			if len(forks) * 3 > fork_branch_limit:
				print("fork_branch_limit exceeding. Terminating now!")
				sys.exit()
			print(f"forking new branch. Current fork branches: {len(forks)*3}")
			new_forks = []
			for recovered_bytes in forks:
				clone_1 = recovered_bytes
				clone_2 = recovered_bytes

				recovered_bytes += byte_v1
				clone_1 += byte_v2
				clone_2 += byte_v3

				temp_forks.append(clone_1)
				temp_forks.append(clone_2)
				temp_forks.append(recovered_bytes)
			forks = temp_forks
			del(temp_forks)
		else:
			# append all the forks with the majority voted byte
			for recovered_bytes in forks:
				recovered_bytes += majority_vote[0]
				temp_forks.append(recovered_bytes)
			try:
				forks = temp_forks
				del(temp_forks)
			except Exception as e:
				raise e

	print("recover_bytes: OK")
	print(f"number of forks: {len(forks)}")
	return forks


def check_sum(file_bytes, original_sha256sum):
	sha256_hash = hashlib.sha256()
	sha256_hash.update(file_bytes)
	version_hash = sha256_hash.hexdigest()
	if version_hash == original_sha256sum:
		return file_bytes


def check_sum_fork_list(recovery_fork_list, original_sha256sum):
	""" Iterate through the list of reconstructed versions 
	and look if checksum matches with the original hash """

	print("check_sum_fork_list running...")
	sha256_hash = hashlib.sha256()
	attempt = 0
	for file_bytes in recovery_fork_list:
		try:
			file_bytes = check_sum(file_bytes, original_sha256sum)
			if file_bytes:
				print(f"Found checksum match. hash attempt: {attempt}")
				return file_bytes
			attempt += 1
		except Exception as e:
			raise e
	print(f"matching checksum not found! Terminating after number of attempts: {attempt}")
	sys.exit()


def main():
	# we have the sha256sum of the original file

	# Load three corrupted versions of the same file
	file1, file2, file3 = load_files_from_dir(corrupted_dir)
	recovery_forks = recover_bytes_2_of_3(file1, file2, file3)
	recovered_bytes = check_sum_fork_list(recovery_forks, original_sha256sum)

	if not recovered_bytes:
		print("not recover_bytes. Terminating")
		sys.exit()
	
	# create the file on disk
	write_recover_file(recovered_bytes, recovery_filepath)
	print("Recovery Done!")


if __name__ == '__main__':
	main()
