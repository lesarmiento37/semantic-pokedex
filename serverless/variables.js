module.exports.subnetIds = (() => {
  const value = process.env.LAMBDA_SUBNET_IDS || '';
  return value
    .split(',')
    .map((v) => v.trim())
    .filter((v) => v.length > 0);
})();
