import numpy as np
import utils
import matplotlib.pyplot as plt
from task3a import pre_process_images
from trainer import BaseTrainer
from task3a import cross_entropy_loss, SoftmaxModel, one_hot_encode
np.random.seed(0)

class SoftmaxTrainer(BaseTrainer):

    def train_step(self, X_batch: np.ndarray, Y_batch: np.ndarray):
        """
        Perform forward, backward and gradient descent step here.
        The function is called once for every batch (see trainer.py) to perform the train step.
        The function returns the mean loss value which is then automatically logged in our variable self.train_history.

        Args:
            X: one batch of images
            Y: one batch of labels
        Returns:
            loss value (float) on batch
        """
        outputs = self.model.forward(X_batch)
        self.model.backward(X_batch, outputs, Y_batch)
        self.model.w = self.model.w - self.learning_rate * self.model.grad
        loss = cross_entropy_loss(Y_batch, outputs)
        return loss

    def validation_step(self):
        """
        Perform a validation step to evaluate the model at the current step for the validation set.
        Also calculates the current accuracy of the model on the train set.
        Returns:
            loss (float): cross entropy loss over the whole dataset
            accuracy_ (float): accuracy over the whole dataset
        Returns:
            loss value (float) on batch
            accuracy_train (float): Accuracy on train dataset
            accuracy_val (float): Accuracy on the validation dataset
        """
        logits = self.model.forward(self.X_val)
        loss = cross_entropy_loss(self.Y_val, logits)

        accuracy_train = calculate_accuracy(
            self.X_train, self.Y_train, self.model)
        accuracy_val = calculate_accuracy(
            self.X_val, self.Y_val, self.model)
        return loss, accuracy_train, accuracy_val
    
def calculate_accuracy(X: np.ndarray, targets: np.ndarray, model: SoftmaxModel) -> float:
    """
    Args:
        X: images of shape [batch size, 785]
        targets: labels/targets of each image of shape: [batch size, 10]
        model: model of class SoftmaxModel
    Returns:
        Accuracy (float)
    """
    correctPredictions = 0 
    totalPredictions = targets.shape[0]
    outputs = model.forward(X)
    for n in range(totalPredictions):
        if outputs[n].argmax() == targets[n].argmax():
            correctPredictions += 1
    accuracy = correctPredictions/totalPredictions
    return accuracy


def main():
    num_epochs = 50
    learning_rate = 0.01
    batch_size = 128
    l2_reg_lambda = 0
    shuffle_dataset = True

    # Load dataset
    X_train, Y_train, X_val, Y_val = utils.load_full_mnist()
    X_train = pre_process_images(X_train)
    X_val = pre_process_images(X_val)
    Y_train = one_hot_encode(Y_train, 10)
    Y_val = one_hot_encode(Y_val, 10)

    # ANY PARTS OF THE CODE BELOW THIS CAN BE CHANGED.

    # Intialize model
    model = SoftmaxModel(l2_reg_lambda)
    # Train model
    trainer = SoftmaxTrainer(
        model, learning_rate, batch_size, shuffle_dataset,
        X_train, Y_train, X_val, Y_val,
    )
    train_history, val_history = trainer.train(num_epochs)

    print("Final Train Cross Entropy Loss:",
          cross_entropy_loss(Y_train, model.forward(X_train)))
    print("Final Validation Cross Entropy Loss:",
          cross_entropy_loss(Y_val, model.forward(X_val)))
    print("Final Train accuracy:", calculate_accuracy(X_train, Y_train, model))
    print("Final Validation accuracy:", calculate_accuracy(X_val, Y_val, model))

    plt.ylim([0.2, .8])
    utils.plot_loss(train_history["loss"],
                    "Training Loss", npoints_to_average=10)
    utils.plot_loss(val_history["loss"], "Validation Loss")
    plt.legend()
    plt.xlabel("Number of Training Steps")
    plt.ylabel("Cross Entropy Loss - Average")
    plt.savefig("task3b_softmax_train_loss.png")
    plt.show()

    # Plot accuracy
    plt.ylim([0.89, .93])
    utils.plot_loss(train_history["accuracy"], "Training Accuracy")
    utils.plot_loss(val_history["accuracy"], "Validation Accuracy")
    plt.xlabel("Number of Training Steps")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.savefig("task3b_softmax_train_accuracy.png")
    plt.show()



    # Training a model with L2 regularization

    model1 = SoftmaxModel(l2_reg_lambda=1.0)
    trainer = SoftmaxTrainer(model1, learning_rate, batch_size, shuffle_dataset,X_train, Y_train, X_val, Y_val,)
    train_history_reg01, val_history_reg01 = trainer.train(num_epochs)
    # You can finish the rest of task 4 below this point.
    # Plotting of softmax weights (Task 4b)
    #plt.imsave("task4b_softmax_weight.png", weight, cmap="gray")

    weights = model.w.T
    image = weights[0][:784]
    image.shape = (image.size//28, 28)
    for i in range(1, 10):
        im = weights[i][:784]
        im.shape = (im.size//28, 28)
        image = np.hstack((image, im))

    weights1 = model1.w.T
    image1 = weights1[0][:784]
    image1.shape = (image1.size//28, 28)
    for i in range(1, 10):
        im = weights1[i][:784]
        im.shape = (im.size//28, 28)
        image1 = np.hstack((image1, im))

    #Normalize the images
    image = image/np.max(image)
    image1 = image1/np.max(image1)

    plt.imsave("image.png", image, cmap="gray")
    plt.imsave("image1.png", image1, cmap="gray")

    image = np.vstack((image, image1))

    plt.imsave("task4b_softmax_weight.png", image, cmap="gray")
    plt.imshow(image, cmap="gray")
    plt.show()





    # Plotting of accuracy for difference values of lambdas
    l2_lambdas = [1, .1, .01, .001]
    plt.ylim([0.7, 1.])
    #utils.plot_loss(train_history["accuracy"], "Training Accuracy")
    l2_norm = [0., 0., 0., 0.]
    for m in range(len(l2_lambdas)):
        model = SoftmaxModel(l2_reg_lambda=l2_lambdas[m])
        trainer = SoftmaxTrainer(model, learning_rate, batch_size, shuffle_dataset,X_train, Y_train, X_val, Y_val,)
        train_history_reg0, val_history = trainer.train(num_epochs)
        l2_norm[m] = np.linalg.norm(model.w, ord=2)
        utils.plot_loss(val_history["accuracy"], "L2_lambda = " + str(l2_lambdas[m]))
        print()
    
    plt.xlabel("Number of Training Steps")
    plt.ylabel("Accuracy")  
    plt.legend()
    plt.savefig("task4c_l2_reg_accuracy.png")
    plt.show()


    # Plotting of the l2 norm for each weight
    plt.plot(l2_lambdas, l2_norm)
    plt.xlabel("Lambda")
    plt.ylabel("L2 Norm")  
    plt.legend()
    plt.savefig("task4d_l2_reg_norms.png")
    plt.show()

if __name__ == "__main__":
    main()