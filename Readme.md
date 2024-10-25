# ConfigDroid

We propose ConfigDroid, which pre-configures global information to determine the candidate set of nodes, reduces the consumption of large models, further enhances the confidence in the test paths of automated testing tools, and provides targeted suggestions for repairing automated test paths.

## Source Code

You can find the source code in the `./ConfigDroid/` directory.

## Requirements

- Android emulator
- Ubuntu or Windows
- Appium Desktop Client: [Download Link](https://github.com/appium/appium-desktop/releases/tag/v1.22.3-4)
- Python 3.7

### Python Dependencies

The following Python packages are required:

- lxml==4.8.0
- opencv-python==4.5.5.64
- sentence-transformers==1.0.3
- torch==1.6.0
- torchvision==0.7.0
- xmltodict==0.12.0
- uiautomator2==2.13.0
- loguru==0.5.3
- openai==0.27.0

You can install these dependencies using the provided `requirements.txt` file.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/Testing-config/ConfigDroid.git
    cd ConfigDroid
    ```

2. Install the required Python packages:

    ```sh
    pip install -r requirements.txt
    ```

3. Install and set up the Appium Desktop Client from the [link](https://github.com/appium/appium-desktop/releases/tag/v1.22.3-4).

4.  Set your `OPENAI_API_KEY` in the `params` file Or Set your `OPENAI_API_KEY` environment variable by adding the following line into your shell initialization script (e.g. `.bashrc`, `.zshrc`, etc.) or running it in the command line:

    ```sh
    export OPENAI_API_KEY="<YOUR_OPENAI_API_KEY>"
    ```
