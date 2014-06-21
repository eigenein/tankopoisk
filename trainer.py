#!/usr/bin/env python3
# coding: utf-8

import sys; sys.dont_write_bytecode = True

import argparse

import numpy
import scipy.sparse

import utils


def main(args):
    _, *tank_ids = next(args.stats)
    num_tanks = len(tank_ids)
    print("[ OK ] %d tanks." % num_tanks)
    print("[INFO] %d features." % args.num_features)

    print("[INFO] Reading stats.")
    y_shape = (num_tanks, args.num_accounts)
    print("[INFO] Y shape: %r." % (y_shape, ))
    account_ids, y, r = [], numpy.ndarray(y_shape), numpy.ndarray(y_shape)

    for j, row in enumerate(args.stats):
        if j % 10000 == 0:
            print("[ OK ] %d rows read." % j)
        if j == args.num_accounts:
            break

        account_id, *row = row
        account_ids.append(int(account_id))

        for i, rating in enumerate(row):
            if rating:
                y[i, j] = float(rating)
                r[i, j] = 1.0

    print("[INFO] Y shape: %r." % (y.shape, ))
    print("[INFO] R shape: %r." % (r.shape, ))

    print("[INFO] Feature normalization.")
    mean = y.sum(1) / r.sum(1)
    mean = numpy.nan_to_num(mean)
    mean = mean.reshape((mean.size, 1))
    y = (y - mean) * r
    print("[INFO] Y: %s" % y)

    x = numpy.random.rand(num_tanks, args.num_features)
    print("[INFO] X shape: %r." % (x.shape, ))
    theta = numpy.random.rand(args.num_accounts, args.num_features)
    print("[INFO] Theta shape: %r." % (theta.shape, ))

    alpha, previous_cost = 0.001, float("+inf")

    print("[INFO] Gradient descent.")
    for i in range(args.num_iterations):
        x, theta = do_step(x, theta, y, r, args.lambda_, alpha)
        current_cost = cost(x, theta, y, r, args.lambda_)

        if i % 1000 == 0:
            print("[INFO] Step #%d." % i)
            print("[INFO] Previous cost: %.3f." % previous_cost)
            print("[INFO] Cost: %.3f." % current_cost)
            print("[INFO] Alpha: %f." % alpha)

        if current_cost < previous_cost:
            alpha *= 1.00  # TODO: 1.01
        else:
            print("[WARN] Step: #%d." % i)
            print("[WARN] Reset alpha: %f." % alpha)
            print("[WARN] Cost: %.3f." % current_cost)
            alpha *= 0.5

        previous_cost = current_cost


def cost(x, theta, y, r, lambda_):
    return (((x.dot(theta.T) - y) * r) ** 2).sum() / 2.0 + lambda_ * (theta ** 2).sum() / 2.0 + lambda_ * (x ** 2).sum() / 2.0


def do_step(x, theta, y, r, lambda_, alpha):
    diff = (x.dot(theta.T) - y) * r
    x_grad = diff.dot(theta) + lambda_ * x
    theta_grad = diff.T.dot(x) + lambda_ * theta
    return (x - alpha * x_grad, theta - alpha * theta_grad)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="stats", help="input file", metavar="<stats.csv.gz>", type=utils.CsvReaderGZipFileType())
    parser.add_argument("--lambda", default=1.0, dest="lambda_", help="regularization parameter (default: %(default)s)", metavar="<lambda>", type=float)
    parser.add_argument("--num-features", default=16, dest="num_features", help="number of features (default: %(default)s)", metavar="<number of features>", type=int)
    parser.add_argument("--num-accounts", default=500000, dest="num_accounts", help="number of accounts to read (default: %(default)s)", metavar="<number of accounts>", type=int)
    parser.add_argument("--num-iterations", default=1000000, dest="num_iterations", help="number of gradient descent iterations (default: %(default)s)", metavar="<number of iterations>", type=int)
    try:
        main(parser.parse_args())
    except KeyboardInterrupt:
        pass
