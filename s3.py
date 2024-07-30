import boto3
import hashlib
import json
from aws_lambda_powertools import Logger
logger = Logger()


# ----- A resource representing Amazon Simple Storage Service (S3) -----
aws_client = boto3.client('s3', region_name='us-east-1')


def s3_get(bucket_name: str, key: str):
    """
    Get file to S3 bucket.

    bucket_name: S3 bucket name.
    key: S3 key path.

    return aws_result (binary)
    """
    try:
        # 1パートづつオブジェクトを取得。
        objects = []
        part_count = 1
        while part_count == 1 or ('PartsCount' in obj and part_count <= obj['PartsCount']):
            # デバッグ用
            logger.debug(f"part_count:{part_count}")

            obj = aws_client.get_object(
                Bucket=bucket_name,
                Key=key,
                PartNumber=part_count,
            )
            objects.append(obj)
            part_count += 1

        # ETagから"-"で分割した先頭の値(ハッシュ値)を抽出する。
        etag = json.loads(obj['ResponseMetadata']['HTTPHeaders']['etag'])
        etag = etag.split('-')[0]

        # 返却するオブジェクトとチェックサムの算出元の値を取り出す。
        if len(objects) == 1:
            # objectsの数が1の場合、マルチパートアップロードではないので、objects[0]を読み取る。
            aws_result = objects[0]['Body'].read()
            # チェックサムの算出元はオブジェクト丸ごと。
            source_bytes = aws_result

        else:
            # マルチパートアップロードの場合、分割されたオブジェクトを順番に読み取って本来の返却値を成形していく。
            aws_result = b''
            source_bytes = b''
            for obj in objects:
                body = obj['Body'].read()
                # 返却するオブジェクトは単純に連結していく。
                aws_result += body
                # チェックサムの算出元はhex表記でないハッシュ値を算出し連結していく。
                source_bytes += hashlib.md5(body).digest()

        # hex表記のハッシュ値を算出。
        checksum = hashlib.md5(source_bytes).hexdigest()

        # チェックサムを比較。
        if etag != checksum:
            raise SystemError("Failed to verify checksum.")

    except SystemError as e:
        # Error if verify checksum failed.
        # output warning log.
        logger.warning(str(e))
        # throw exception.
        raise
    except Exception:
        # Error if get failed.
        # output warning log.
        logger.warning("Failed to get a object.")
        # throw exception.
        raise
    else:
        # Return a object body.
        return aws_result
